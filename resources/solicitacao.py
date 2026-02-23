from datetime import datetime
import pytz
from flask import request
from flask_restful import Resource
from models import Solicitacao, Notificacao, Usuario, Propriedade, Agricultor, Servico
from helpers.database import db
from helpers.auditoria.auditoria import registrar_log
from marshmallow import ValidationError
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from schemas import (
    SolicitacaoDetalhadoSchema,
    SolicitacaoListaSchema,
    SolicitacaoLoadSchema
)

# Inicialização dos Schemas baseados no arquivo de definições
solicitacao_schema_detalhado = SolicitacaoDetalhadoSchema()
solicitacoes_schema_lista = SolicitacaoListaSchema(many=True)
solicitacao_schema_carga = SolicitacaoLoadSchema()

def obter_agora_brasil():
    """Garante o registro do horário correto no banco de dados"""
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    return datetime.now(fuso_brasil).replace(tzinfo=None)

class SolicitacaoListResource(Resource):
    def get(self):
        """Lista solicitações com filtros para o painel administrativo"""
        operador_id = request.args.get('operador_id')
        agricultor_id = request.args.get('agricultor_id') 
        status = request.args.get('status')
        
        query = Solicitacao.query
        if operador_id: query = query.filter_by(operador_id=operador_id)
        if agricultor_id: query = query.filter_by(agricultor_id=agricultor_id)
        if status: query = query.filter_by(status=status)
            
        return solicitacoes_schema_lista.dump(query.all()), 200

    def post(self):
        """Cria uma solicitação e notifica apenas a Gestão"""
        json_data = request.get_json()
        try:
            data = solicitacao_schema_carga.load(json_data)
            propriedade = Propriedade.query.get(data['propriedade_id'])
            
            if not propriedade:
                return {"message": "A propriedade informada não existe."}, 404

            # Validação de segurança: o agricultor deve ser o dono da terra
            if int(propriedade.agricultor_id) != int(data['agricultor_id']):
                return {"message": "Acesso negado: propriedade pertence a outro agricultor."}, 403
            
            # Evita pedidos duplicados em aberto
            pedido_duplicado = Solicitacao.query.filter(
                and_(
                    Solicitacao.agricultor_id == data['agricultor_id'],
                    Solicitacao.propriedade_id == data['propriedade_id'],
                    Solicitacao.servico_id == data['servico_id'],
                    Solicitacao.status.in_(['Pendente', 'Em Andamento', 'EM ANDAMENTO'])
                )
            ).first()

            if pedido_duplicado:
                return {"message": "Você já tem um pedido em aberto para este serviço."}, 409

            nova_solicitacao = Solicitacao(data_solicitacao=obter_agora_brasil(), **data)
            db.session.add(nova_solicitacao)
            db.session.commit()
            
            # --- NOTIFICAÇÃO DE NOVO PEDIDO (Apenas Admins/Gestores) ---
            try:
                agri_obj = Agricultor.query.get(data['agricultor_id'])
                serv_obj = Servico.query.get(data['servico_id'])
                msg_admin = f"Nova solicitação de {serv_obj.nome_servico} feita por {agri_obj.nome}."

                equipe_gestao = Usuario.query.filter(Usuario.perfil.in_(['admin', 'gestor', 'ADMIN', 'GESTOR'])).all()
                for membro in equipe_gestao:
                    db.session.add(Notificacao(usuario_id=membro.id, mensagem=msg_admin))
                db.session.commit()
            except Exception as e:
                print(f"Erro Notificação Post: {e}")

            try:
                # Associamos ao usuário do agricultor se possível, senão vai vazio
                user_id = agri_obj.usuario_id if agri_obj else None 
                registrar_log(
                    acao="CRIAR",
                    tabela="Solicitacao",
                    registro_id=nova_solicitacao.id,
                    usuario_id=user_id,
                    detalhes=f"Solicitação criada para a propriedade ID {nova_solicitacao.propriedade_id}"
                )
            except Exception as e:
                print(f"Erro ao registrar auditoria (CRIAR): {e}")

            try:
                # Associamos ao usuário do agricultor se possível, senão vai vazio
                user_id = agri_obj.usuario_id if agri_obj else None 
                registrar_log(
                    acao="CRIAR",
                    tabela="Solicitacao",
                    registro_id=nova_solicitacao.id,
                    usuario_id=user_id,
                    detalhes=f"Solicitação criada para a propriedade ID {nova_solicitacao.propriedade_id}"
                )
            except Exception as e:
                print(f"Erro ao registrar auditoria (CRIAR): {e}")

            return solicitacao_schema_detalhado.dump(nova_solicitacao), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400

class SolicitacaoResource(Resource):
    def get(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        return solicitacao_schema_detalhado.dump(solicitacao), 200

    def put(self, solicitacao_id):
        """Atualiza a solicitação e gera notificações específicas por papel"""
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        
        status_anterior = solicitacao.status
        operador_anterior = solicitacao.operador_id
        
        try:
            data = solicitacao_schema_carga.load(json_data, partial=True)
            
            # Bloqueia alteração de dados base após o início do processo
            if solicitacao.status.lower() != 'pendente':
                for campo in ['agricultor_id', 'propriedade_id', 'servico_id']:
                    if campo in data and str(data[campo]) != str(getattr(solicitacao, campo)):
                        return {"message": "Não é permitido alterar dados base de pedidos processados."}, 400

            # Atualização dos campos
            if 'operador_id' in json_data:
                val = json_data.get('operador_id')
                solicitacao.operador_id = int(val) if val and str(val).strip() != "" else None
            
            if 'veiculo_id' in json_data:
                val = json_data.get('veiculo_id')
                solicitacao.veiculo_id = int(val) if val and str(val).strip() != "" else None

            for key in ['status', 'data_execucao', 'observacao', 'observacao_funcionario', 'observacoes']:
                if key in data: setattr(solicitacao, key, data[key])

            # --- LÓGICA DE NOTIFICAÇÕES PERSONALIZADAS ---
            try:
                serv_obj = Servico.query.get(solicitacao.servico_id)
                nome_servico = (serv_obj.nome_servico if serv_obj else "serviço").lower()
                local = solicitacao.propriedade.terreno if solicitacao.propriedade else "propriedade"

                # 1. ATRIBUÍDO A UM FUNCIONÁRIO (Informa o local)
                if solicitacao.operador_id and solicitacao.operador_id != operador_anterior:
                    msg_func = f"Você foi escalado para o serviço de {nome_servico} na propriedade {local}."
                    db.session.add(Notificacao(usuario_id=solicitacao.operador_id, mensagem=msg_func))

                # 2. MUDANÇA DE STATUS (Filtra por papel)
                if solicitacao.status != status_anterior:
                    status_limpo = solicitacao.status.strip().upper()
                    
                    # PARA O AGRICULTOR (Usa usuario_id do modelo)
                    if solicitacao.agricultor and solicitacao.agricultor.usuario_id:
                        if status_limpo in ['CONCLUÍDA', 'CONCLUIDA']:
                            msg_produtor = f"O serviço de {nome_servico} foi concluído com sucesso!"
                        else:
                            msg_produtor = f"A sua solicitação de {nome_servico} foi {solicitacao.status.lower()}."
                        db.session.add(Notificacao(usuario_id=solicitacao.agricultor.usuario_id, mensagem=msg_produtor))

                    # PARA O ADMIN/GESTOR (Informa QUEM concluiu)
                    if status_limpo in ['CONCLUÍDA', 'CONCLUIDA']:
                        nome_func = solicitacao.operador.nome if solicitacao.operador else "Um técnico"
                        nome_agri = solicitacao.agricultor.nome if solicitacao.agricultor else "um agricultor"
                        msg_admin = f"O técnico {nome_func} concluiu o serviço de {nome_servico} de {nome_agri}."
                        
                        equipe_gestao = Usuario.query.filter(Usuario.perfil.in_(['admin', 'gestor', 'ADMIN', 'GESTOR'])).all()
                        for membro in equipe_gestao:
                            db.session.add(Notificacao(usuario_id=membro.id, mensagem=msg_admin))

            except Exception as e:
                print(f"Erro ao processar notificações: {e}")

            db.session.commit()

            try:
                # Determina o texto dos detalhes baseado na alteração
                detalhes_audit = "Solicitação atualizada."
                if solicitacao.status != status_anterior:
                    detalhes_audit = f"Status alterado de '{status_anterior}' para '{solicitacao.status}'."
                
                # Tenta pegar quem alterou (geralmente passado como operador_id no JSON do front)
                operador_q_alterou = json_data.get('operador_id')

                registrar_log(
                    acao="EDITAR",
                    tabela="Solicitacao",
                    registro_id=solicitacao.id,
                    usuario_id=operador_q_alterou,
                    detalhes=detalhes_audit
                )
            except Exception as e:
                print(f"Erro ao registrar auditoria (EDITAR): {e}")

            return solicitacao_schema_detalhado.dump(solicitacao), 200
            
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao atualizar", "detalhe": str(e)}, 500

    def delete(self, solicitacao_id):
        """Remove solicitações apenas se ainda estiverem pendentes"""
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        if solicitacao.status.lower() != 'pendente':
            return {"message": "Ação Proibida: Pedido já processado."}, 400
        
        # captura dados antes de excluir para usar na auditoria
        id_temp = solicitacao.id
        agri_temp = solicitacao.agricultor_id

        db.session.delete(solicitacao)
        db.session.commit()

        try:
            registrar_log(
                acao="EXCLUIR",
                tabela="Solicitacao",
                registro_id=id_temp,
                usuario_id=None, # Exclusões são feitas por quem está logado, aqui garantimos pelo menos o registo da ação
                detalhes=f"Solicitação do agricultor ID {agri_temp} foi excluída permanentemente."
            )
        except Exception as e:
            print(f"Erro ao registrar auditoria (EXCLUIR): {e}")

        return '', 204