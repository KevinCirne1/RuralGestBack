from flask import request
from flask_restful import Resource
# CORREÇÃO AQUI: db vem de helpers.database, não de models
from helpers.database import db
from models import Solicitacao, Notificacao, Usuario
from marshmallow import ValidationError
from schemas import (
    SolicitacaoDetalhadoSchema,
    SolicitacaoListaSchema,
    SolicitacaoLoadSchema
)

# Instâncias dos Schemas
solicitacao_schema_detalhado = SolicitacaoDetalhadoSchema()
solicitacoes_schema_lista = SolicitacaoListaSchema(many=True)
solicitacao_schema_carga = SolicitacaoLoadSchema()

class SolicitacaoListResource(Resource):
    def get(self):
        # Ordena por data (mais recentes primeiro)
        solicitacoes = Solicitacao.query.order_by(Solicitacao.data_solicitacao.desc()).all()
        return solicitacoes_schema_lista.dump(solicitacoes)

    def post(self):
        json_data = request.get_json()
        print(f"📥 Dados recebidos no POST: {json_data}") # DEBUG

        try:
            data = solicitacao_schema_carga.load(json_data)
            nova_solicitacao = Solicitacao(**data)
            db.session.add(nova_solicitacao)
            db.session.commit()
            
            # --- Notifica Admins ---
            try:
                admins = Usuario.query.filter(Usuario.perfil.in_(['gestor', 'tecnico'])).all()
                if admins:
                    msg = f"Novo Pedido: Solicitação #{nova_solicitacao.id} criada."
                    for admin in admins:
                        db.session.add(Notificacao(usuario_id=admin.id, mensagem=msg))
                    db.session.commit()
            except Exception as e:
                print(f"❌ Erro ao notificar admins: {e}")
            # -----------------------

            return solicitacao_schema_detalhado.dump(nova_solicitacao), 201

        except ValidationError as err:
            print(f"❌ Erro de Validação (POST): {err.messages}")
            return {"messages": err.messages, "message": "Erro nos dados enviados."}, 400
        except Exception as e:
            print(f"❌ Erro Interno (POST): {e}")
            return {"message": "Erro interno no servidor."}, 500

class SolicitacaoResource(Resource):
    def get(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        return solicitacao_schema_detalhado.dump(solicitacao)

    def put(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        print(f"📥 Dados recebidos no PUT (ID {solicitacao_id}): {json_data}") # DEBUG
        
        try:
            # partial=True permite enviar só alguns campos se quiser
            data = solicitacao_schema_carga.load(json_data, partial=True)
            
            novo_status = data.get('status')
            
            # Atualiza os campos no banco
            for key, value in data.items():
                setattr(solicitacao, key, value)
            
            # --- LÓGICA DE VEÍCULO ---
            if novo_status == 'APROVADA' and solicitacao.veiculo:
                solicitacao.veiculo.status = 'EM_USO'
            elif novo_status in ['CONCLUÍDA', 'RECUSADA', 'CANCELADA'] and solicitacao.veiculo:
                solicitacao.veiculo.status = 'DISPONIVEL'
            # -------------------------
            
            db.session.commit()

            # --- Notifica Agricultor ---
            if novo_status in ['APROVADA', 'RECUSADA', 'CONCLUÍDA']:
                try:
                    agricultor = solicitacao.agricultor
                    if agricultor and hasattr(agricultor, 'usuario_id') and agricultor.usuario_id:
                        msg = f"Sua solicitação #{solicitacao.id} foi {novo_status}."
                        if novo_status == 'RECUSADA' and solicitacao.motivo_recusa:
                            msg += f" Motivo: {solicitacao.motivo_recusa}"
                        
                        db.session.add(Notificacao(usuario_id=agricultor.usuario_id, mensagem=msg))
                        db.session.commit()
                except Exception as e:
                    print(f"⚠️ Erro ao notificar agricultor: {e}")
            # ---------------------------

            return solicitacao_schema_detalhado.dump(solicitacao)

        except ValidationError as err:
            print(f"❌ Erro de Validação (PUT): {err.messages}")
            return {"messages": err.messages, "message": "Erro nos dados enviados."}, 400
        except Exception as e:
            print(f"❌ Erro Interno (PUT): {e}")
            return {"message": f"Erro interno: {str(e)}"}, 500

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        
        if solicitacao.veiculo and solicitacao.status == 'APROVADA':
            solicitacao.veiculo.status = 'DISPONIVEL'
            
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204