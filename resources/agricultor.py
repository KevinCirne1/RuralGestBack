from flask import request
from flask_restful import Resource
from models import Agricultor
from helpers.database import db
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt
from schemas import (
    AgricultorDetalhadoSchema, 
    AgricultorListaSchema, 
    AgricultorLoadSchema
)

# --- Schemas ---
agricultor_schema_detalhado = AgricultorDetalhadoSchema()
agricultores_schema_lista = AgricultorListaSchema(many=True)
agricultor_schema_carga = AgricultorLoadSchema()

# --- Resources ---

class AgricultorListResource(Resource):
    @jwt_required()
    def get(self):
        agricultores = Agricultor.query.all()
        return agricultores_schema_lista.dump(agricultores)

    @jwt_required()
    def post(self):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403

        json_data = request.get_json()
        try:
            # CORREÇÃO: load() agora devolve um dicionário validado
            dados_validados = agricultor_schema_carga.load(json_data)
            # CORREÇÃO: Criamos a instância do modelo manualmente
            novo_agricultor = Agricultor(**dados_validados)

        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.add(novo_agricultor)
        db.session.commit()
        return agricultor_schema_detalhado.dump(novo_agricultor), 201

class AgricultorResource(Resource):
    @jwt_required()
    def get(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        return agricultor_schema_detalhado.dump(agricultor)

    @jwt_required()
    def put(self, agricultor_id):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403

        agricultor = Agricultor.query.get_or_404(agricultor_id)
        json_data = request.get_json()

        try:
            # CORREÇÃO: load() devolve um dicionário validado
            dados_validados = agricultor_schema_carga.load(json_data, partial=True)
            # CORREÇÃO: Atualizamos os atributos do objeto existente
            for key, value in dados_validados.items():
                setattr(agricultor, key, value)

        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.commit()
        return agricultor_schema_detalhado.dump(agricultor)
    
    @jwt_required()
    def delete(self, agricultor_id):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403

        agricultor = Agricultor.query.get_or_404(agricultor_id)
        db.session.delete(agricultor)
        db.session.commit()
        return '', 204