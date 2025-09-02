from flask import request
from flask_restful import Resource
from models import Agricultor
from helpers.database import db
from marshmallow import ValidationError
# CORREÇÃO: Importamos as CLASSES dos schemas
from schemas import (
    AgricultorDetalhadoSchema, 
    AgricultorListaSchema, 
    AgricultorLoadSchema
)

# --- Instâncias dos Schemas ---
agricultor_schema_detalhado = AgricultorDetalhadoSchema()
agricultores_schema_lista = AgricultorListaSchema(many=True)
agricultor_schema_carga = AgricultorLoadSchema()

# --- Resources ---

class AgricultorListResource(Resource):
    def get(self):
        agricultores = Agricultor.query.all()
        return agricultores_schema_lista.dump(agricultores)

    def post(self):
        json_data = request.get_json()
        try:
            dados_validados = agricultor_schema_carga.load(json_data)
            novo_agricultor = Agricultor(**dados_validados)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.add(novo_agricultor)
        db.session.commit()
        return agricultor_schema_detalhado.dump(novo_agricultor), 201

class AgricultorResource(Resource):
    def get(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        return agricultor_schema_detalhado.dump(agricultor)

    def put(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        json_data = request.get_json()
        try:
            dados_validados = agricultor_schema_carga.load(json_data, partial=True)
            for key, value in dados_validados.items():
                setattr(agricultor, key, value)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.commit()
        return agricultor_schema_detalhado.dump(agricultor)

    def delete(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        db.session.delete(agricultor)
        db.session.commit()
        return '', 204