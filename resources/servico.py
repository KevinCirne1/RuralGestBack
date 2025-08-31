from flask import request
from flask_restful import Resource
from models import Servico
from helpers.database import db
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt
from schemas import (
    ServicoListaSchema,
    ServicoLoadSchema
)

# --- Schemas ---
servicos_schema_lista = ServicoListaSchema(many=True)
servico_schema_carga = ServicoLoadSchema()

# --- Resources ---

class ServicoListResource(Resource):
    @jwt_required()
    def get(self):
        servicos = Servico.query.all()
        return servicos_schema_lista.dump(servicos)

    @jwt_required()
    def post(self):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403
            
        json_data = request.get_json()
        try:
            dados_validados = servico_schema_carga.load(json_data)
            novo_servico = Servico(**dados_validados)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.add(novo_servico)
        db.session.commit()
        return ServicoListaSchema().dump(novo_servico), 201

class ServicoResource(Resource):
    @jwt_required()
    def get(self, servico_id):
        servico = Servico.query.get_or_404(servico_id)
        return ServicoListaSchema().dump(servico)

    @jwt_required()
    def delete(self, servico_id):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403
            
        servico = Servico.query.get_or_404(servico_id)
        db.session.delete(servico)
        db.session.commit()
        return '', 204