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
            status_antigo = solicitacao.status
            
            # Atualiza os campos enviados
            for key, value in data.items():
                setattr(solicitacao, key, value)
            
            # --- AUTOMAÇÃO DE DATA DE EXECUÇÃO ---
            # Lista de status que indicam fim de serviço
            status_fim = ['Concluída', 'Concluida', 'CONCLUÍDA', 'Finalizada']
            
            # Se o status é de conclusão E o usuário não enviou uma data manual:
            if solicitacao.status in status_fim and 'data_execucao' not in json_data:
                solicitacao.data_execucao = datetime.now()
                print(f"DEBUG: Data de execução preenchida automaticamente para {solicitacao.data_execucao}")
            # -------------------------------------

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
