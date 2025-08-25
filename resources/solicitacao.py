from flask import request
from flask_restful import Resource
from models.solicitacao import Solicitacao
from helpers.database import db, ma
from marshmallow import fields, ValidationError

# --- Schemas ---
class SolicitacaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Solicitacao
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    data_solicitacao = fields.DateTime(dump_only=True)
    agricultor_id = fields.Int(required=True)
    propriedade_id = fields.Int(required=True)
    servico_id = fields.Int(required=True)

solicitacao_schema = SolicitacaoSchema()
solicitacoes_schema = SolicitacaoSchema(many=True)

# --- Resources ---
class SolicitacaoListResource(Resource):
    def get(self):
        return solicitacoes_schema.dump(Solicitacao.query.all())
    def post(self):
        json_data = request.get_json()
        try:
            # TODO: Validar se o agricultor_id, propriedade_id e servico_id existem
            solicitacao = solicitacao_schema.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        db.session.add(solicitacao)
        db.session.commit()
        return solicitacao_schema.dump(solicitacao), 201

class SolicitacaoResource(Resource):
    def get(self, solicitacao_id):
        return solicitacao_schema.dump(Solicitacao.query.get_or_404(solicitacao_id))
    def put(self, solicitacao_id): # Atualizar status ou operador
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        solicitacao.status = json_data.get('status', solicitacao.status)
        solicitacao.operador_id = json_data.get('operador_id', solicitacao.operador_id)
        db.session.commit()
        return solicitacao_schema.dump(solicitacao)
    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204
