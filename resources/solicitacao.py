from datetime import datetime
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

solicitacao_schema_detalhado = SolicitacaoDetalhadoSchema()
solicitacoes_schema_lista = SolicitacaoListaSchema(many=True)
solicitacao_schema_carga = SolicitacaoLoadSchema()

class SolicitacaoListResource(Resource):
    def get(self):
        solicitacoes = Solicitacao.query.all()
        return solicitacoes_schema_lista.dump(solicitacoes)

    def post(self):
        json_data = request.get_json()
        print(f"\n--- DEBUG POST SOLICITACAO ---")
        print(f"Dados: {json_data}")
        
        try:
            data = solicitacao_schema_carga.load(json_data)
            nova_solicitacao = Solicitacao(data_solicitacao=datetime.now(), **data)
            db.session.add(nova_solicitacao)
            db.session.commit()
            
            # Notificação de Admins
            try:
                admins = Usuario.query.filter(Usuario.perfil.in_(['gestor', 'tecnico'])).all()
                for admin in admins:
                    db.session.add(Notificacao(usuario_id=admin.id, mensagem="Novo Pedido de Serviço Criado"))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Aviso: Erro na notificação: {e}")

            return solicitacao_schema_detalhado.dump(nova_solicitacao), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400
        except Exception as e:
            db.session.rollback()
            print(f"ERRO CRÍTICO: {str(e)}")
            return {"message": "Erro interno", "detalhe": str(e)}, 500


class SolicitacaoResource(Resource):
    def get(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        return solicitacao_schema_detalhado.dump(solicitacao)

    def put(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        try:
            data = solicitacao_schema_carga.load(json_data, partial=True)
            
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
            return solicitacao_schema_detalhado.dump(solicitacao)
        except ValidationError as err:
            return {"messages": err.messages}, 400

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204