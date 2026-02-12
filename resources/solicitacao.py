from datetime import datetime
import pytz
from flask import request
from flask_restful import Resource
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from models import Solicitacao, Notificacao, Usuario, Propriedade, Agricultor, Servico
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

# Função para garantir o horário de Brasília
def obter_agora_brasil():
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    return datetime.now(fuso_brasil).replace(tzinfo=None)

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
        """Cria uma nova solicitação e notifica a equipe administrativa"""
        json_data = request.get_json()
        
        try:
            data = solicitacao_schema_carga.load(json_data)
            propriedade = Propriedade.query.get(data['propriedade_id'])
            
            if not propriedade:
                return {"message": "A propriedade informada não existe."}, 404

            id_agricultor_enviado = int(data['agricultor_id'])
            id_dono_da_terra = int(propriedade.agricultor_id)

            if id_dono_da_terra != id_agricultor_enviado:
                return {
                    "message": "Acesso negado",
                    "detalhe": {"propriedade_id": "Esta propriedade pertence a outro agricultor."}
                }, 403
            
            pedido_duplicado = Solicitacao.query.filter(
                and_(
                    Solicitacao.agricultor_id == id_agricultor_enviado,
                    Solicitacao.propriedade_id == data['propriedade_id'],
                    Solicitacao.servico_id == data['servico_id'],
                    Solicitacao.status.in_(['Pendente', 'Em Andamento', 'EM ANDAMENTO'])
                )
            ).first()

            if pedido_duplicado:
                return {
                    "message": "Atenção: Você já tem um pedido em aberto para este serviço.",
                    "id_existente": pedido_duplicado.id
                }, 409

            # Criação com hora de Brasília
            nova_solicitacao = Solicitacao(data_solicitacao=obter_agora_brasil(), **data)
            db.session.add(nova_solicitacao)
            
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                return {"message": "Erro de integridade no banco.", "detalhe": str(e)}, 400
            
            # Notificação para Admin
            try:
                agri_obj = Agricultor.query.get(id_agricultor_enviado)
                serv_obj = Servico.query.get(data['servico_id'])
                msg_admin = f"{agri_obj.nome if agri_obj else 'Um agricultor'} solicitou {serv_obj.nome_servico if serv_obj else 'um serviço'}"

                equipe = Usuario.query.filter(Usuario.perfil.in_(['admin', 'gestor', 'tecnico'])).all()
                for membro in equipe:
                    db.session.add(Notificacao(usuario_id=membro.id, mensagem=msg_admin))
                
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Erro Notificação Admin: {e}")

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
        """Atualiza a solicitação e notifica o agricultor"""
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        status_anterior = solicitacao.status
        
        try:
            data = solicitacao_schema_carga.load(json_data, partial=True)
            
            if solicitacao.status.lower() != 'pendente':
                for campo in ['agricultor_id', 'propriedade_id', 'servico_id']:
                    if campo in data and str(data[campo]) != str(getattr(solicitacao, campo)):
                        return {"message": "Não é permitido alterar dados base de pedidos processados."}, 400

            if 'operador_id' in json_data:
                val = json_data.get('operador_id')
                solicitacao.operador_id = int(val) if val and str(val).strip() != "" else None
            
            if 'veiculo_id' in json_data:
                val = json_data.get('veiculo_id')
                solicitacao.veiculo_id = int(val) if val and str(val).strip() != "" else None

            if 'status' in data: solicitacao.status = data['status']
            if 'observacoes' in data: solicitacao.observacoes = data['observacoes']
            if 'data_execucao' in data: solicitacao.data_execucao = data['data_execucao']

            # --- NOTIFICAÇÃO PERSONALIZADA ---
            if solicitacao.status != status_anterior:
                try:
                    agri = Agricultor.query.get(solicitacao.agricultor_id)
                    id_destino = agri.usuario_id if (agri and hasattr(agri, 'usuario_id')) else solicitacao.agricultor_id
                    
                    serv_obj = Servico.query.get(solicitacao.servico_id)
                    nome_servico = serv_obj.nome_servico if serv_obj else "serviço"
                    
                    msg_produtor = f"A sua solicitação de {nome_servico} foi {solicitacao.status.lower()}."
                    
                    # Removido o campo data_criacao daqui para evitar erro de nome de coluna
                    db.session.add(Notificacao(usuario_id=id_destino, mensagem=msg_produtor))
                except Exception as e:
                    print(f"Erro Notificação Produtor: {e}")

            db.session.commit()
            return solicitacao_schema_detalhado.dump(solicitacao), 200
            
        except ValidationError as err:
            return {"errors": err.messages}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao atualizar", "detalhe": str(e)}, 500

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        if solicitacao.status.lower() != 'pendente':
            return {"message": "Ação Proibida: Pedido já processado."}, 400
        
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204