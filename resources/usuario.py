from flask import request
from flask_restful import Resource
from models import Usuario
from helpers.database import db
from marshmallow import ValidationError
from schemas import (
    UsuarioDetalhadoSchema, 
    UsuarioListaSchema, 
    UsuarioLoadSchema
)
from helpers.application import cache, bcrypt

# --- Instâncias dos Schemas ---
usuario_schema_detalhado = UsuarioDetalhadoSchema()
usuarios_schema_lista = UsuarioListaSchema(many=True)
usuario_schema_carga = UsuarioLoadSchema()

# --- Resources ---

class UsuarioListResource(Resource):
    @cache.cached(timeout=600, key_prefix='all_usuarios')
    def get(self):
        usuarios = Usuario.query.all()
        return usuarios_schema_lista.dump(usuarios)

    def post(self):
        json_data = request.get_json()
        try:
            dados_validados = usuario_schema_carga.load(json_data)

            # Criptografar a senha antes de criar o usuário
            senha_texto = dados_validados.get('senha')
            if senha_texto:
                hashed_password = bcrypt.generate_password_hash(senha_texto).decode('utf-8')
                dados_validados['senha'] = hashed_password

            novo_usuario = Usuario(**dados_validados)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        db.session.add(novo_usuario)
        db.session.commit()

        cache.delete('all_usuarios')
        return usuario_schema_detalhado.dump(novo_usuario), 201

class UsuarioResource(Resource):
    @cache.cached(timeout=600, key_prefix='usuario')
    def get(self, usuario_id):
        usuario = Usuario.query.get_or_404(usuario_id)
        return usuario_schema_detalhado.dump(usuario)

    def delete(self, usuario_id):
        usuario = Usuario.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        cache.delete('all_usuarios')
        cache.delete(f'usuario_{usuario_id}')
        return '', 204