from datetime import datetime
import pytz
from flask import request
from flask_restful import Resource
from models import Solicitacao, Notificacao, Usuario, Documento
from helpers.database import db
from marshmallow import ValidationError
from schemas import (
    SolicitacaoDetalhadoSchema,
    SolicitacaoListaSchema,
    SolicitacaoLoadSchema
)

# Inicialização dos Schemas
solicitacao_schema_detalhado = SolicitacaoDetalhadoSchema()
solicitacoes_schema_lista = SolicitacaoListaSchema(many=True)
solicitacao_schema_carga = SolicitacaoLoadSchema()

class SolicitacaoListResource(Resource):
    def get(self):
        """Lista solicitações com filtros opcionais"""
        operador_id = request.args.get('operador_id')
        agricultor_id = request.args.get('agricultor_id') 
        status = request.args.get('status')
        
        query = Solicitacao.query

        if operador_id:
            query = query.filter_by(operador_id=operador_id)
        if agricultor_id:
            query = query.filter_by(agricultor_id=agricultor_id)
        if status:
            query = query.filter_by(status=status)
            
        solicitacoes = query.all()
        return solicitacoes_schema_lista.dump(solicitacoes), 200

    def post(self):
        """Cria uma nova solicitação com validação de posse e notificação personalizada"""
        json_data = request.get_json()
        
        try:
            # 1. Validação do Marshmallow
            data = solicitacao_schema_carga.load(json_data)
            nova_solicitacao = Solicitacao(data_solicitacao=datetime.now(), **data)
            db.session.add(nova_solicitacao)
            db.session.commit()
            
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                return {"message": "Erro de integridade no banco.", "detalhe": str(e)}, 400
            
            # 6. NOTIFICAÇÃO PERSONALIZADA 
            try:
                # Busca os objetos para extrair os nomes reais
                agri_obj = Agricultor.query.get(id_agricultor_enviado)
                serv_obj = Servico.query.get(data['servico_id'])
                
                # Monta a string: "Nome do Agricultor solicitou Nome do Serviço"
                nome_agricultor = agri_obj.nome if agri_obj else "Um agricultor"
                nome_servico = serv_obj.nome_servico if serv_obj else "um serviço"
                
                msg_admin = f"{nome_agricultor} solicitou {nome_servico}"

                # Envia a notificação para todos os gestores e técnicos
                admins = Usuario.query.filter(Usuario.perfil.in_(['gestor', 'tecnico'])).all()
                for admin in admins:
                    db.session.add(Notificacao(usuario_id=admin.id, mensagem=msg_admin))
                
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Aviso: Falha ao gerar notificação: {e}")

            return solicitacao_schema_detalhado.dump(nova_solicitacao), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro interno", "detalhe": str(e)}, 500

class SolicitacaoResource(Resource):
    def get(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        return solicitacao_schema_detalhado.dump(solicitacao), 200

    def put(self, solicitacao_id):
        """Atualiza a solicitação com atribuição FORÇADA de técnico"""
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        
        # DEBUG: Mostra o que chegou do React antes de qualquer validação
        print(f"DEBUG: JSON Bruto Recebido: {json_data}") 

        try:
            # Carrega validações padrão
            data = solicitacao_schema_carga.load(json_data, partial=True)
            
            status_atual_no_banco = solicitacao.status.lower()

            # TRAVA DE SEGURANÇA 
            if status_atual_no_banco != 'pendente':
                campos_bloqueados = ['agricultor_id', 'propriedade_id', 'servico_id']
                for campo in campos_bloqueados:
                    if campo in data:
                        if str(data[campo]) != str(getattr(solicitacao, campo)):
                            return {
                                "message": "Dados Protegidos",
                                "detalhe": f"Não é permitido alterar '{campo}' após processamento."
                            }, 400

            
            raw_operador_id = json_data.get('operador_id')
            
            # Verifica se veio algo (pode ser int ou string numérica)
            if raw_operador_id is not None and str(raw_operador_id) != "":
                print(f"DEBUG: Forçando atualização do OPERADOR para ID {raw_operador_id}")
                solicitacao.operador_id = int(raw_operador_id)

            # Mesma coisa para o veículo
            raw_veiculo_id = json_data.get('veiculo_id')
            if raw_veiculo_id is not None and str(raw_veiculo_id) != "":
                solicitacao.veiculo_id = int(raw_veiculo_id)

            # Campos normais continuam via Schema
            if 'status' in data:
                solicitacao.status = data['status']
            
            if 'observacoes' in data:
                solicitacao.observacoes = data['observacoes']

            if 'data_execucao' in data:
                solicitacao.data_execucao = data['data_execucao']

            # Notificação 
            if 'status' in data and data['status'] != solicitacao.status:
                if solicitacao.agricultor and solicitacao.agricultor.usuario_id:
                    msg = f"Sua solicitação mudou para: {solicitacao.status}"
                    db.session.add(Notificacao(usuario_id=solicitacao.agricultor.usuario_id, mensagem=msg))

            db.session.commit()
            
            return solicitacao_schema_detalhado.dump(solicitacao), 200
            
        except ValidationError as err:
            return {"messages": err.messages}, 400
        except Exception as e:
            db.session.rollback()
            print(f"ERRO NO PUT: {e}")
            return {"message": "Erro interno", "detalhe": str(e)}, 500

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        
        if solicitacao.status.lower() != 'pendente':
            return {
                "message": "Ação Proibida",
                "detalhe": "Não é possível excluir uma solicitação que já foi processada."
            }, 400
        
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204
