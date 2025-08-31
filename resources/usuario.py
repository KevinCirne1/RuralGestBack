from flask import request
from flask_restful import Resource
from models import Usuario
from helpers.database import db
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt
from schemas import (
    UsuarioListaSchema,
    UsuarioLoadSchema
)

# --- Schemas ---
usuarios_schema_lista = UsuarioListaSchema(many=True)
usuario_schema_carga = UsuarioLoadSchema()

# --- Resources ---

class UsuarioListResource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403
        
        usuarios = Usuario.query.all()
        return usuarios_schema_lista.dump(usuarios)

    @jwt_required()
    def post(self):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403

        json_data = request.get_json()
        
        try:
            dados_validados = usuario_schema_carga.load(json_data)
            senha = dados_validados.pop('senha')
            dados_validados["senha_hash"] = generate_password_hash(senha)
            novo_usuario = Usuario(**dados_validados)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.add(novo_usuario)
        db.session.commit()
        return UsuarioListaSchema().dump(novo_usuario), 201

class UsuarioResource(Resource):
    @jwt_required()
    def get(self, usuario_id):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403

        usuario = Usuario.query.get_or_404(usuario_id)
        return UsuarioListaSchema().dump(usuario)

    @jwt_required()
    def delete(self, usuario_id):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403

        usuario = Usuario.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204
