from flask import request
from flask_restful import Resource
from models.solicitacao import Solicitacao
from helpers.database import db, ma
from marshmallow import fields, ValidationError
from flask_jwt_extended import jwt_required

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
    @jwt_required()
    def get(self):
        return solicitacoes_schema.dump(Solicitacao.query.all())
    
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        try:
            solicitacao = solicitacao_schema.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        db.session.add(solicitacao)
        db.session.commit()
        return solicitacao_schema.dump(solicitacao), 201

class SolicitacaoResource(Resource):
    @jwt_required()
    def get(self, solicitacao_id):
        return solicitacao_schema.dump(Solicitacao.query.get_or_404(solicitacao_id))
    
    @jwt_required()
    def put(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        solicitacao.status = json_data.get('status', solicitacao.status)
        solicitacao.operador_id = json_data.get('operador_id', solicitacao.operador_id)
        db.session.commit()
        return solicitacao_schema.dump(solicitacao)
    
    @jwt_required()
    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204