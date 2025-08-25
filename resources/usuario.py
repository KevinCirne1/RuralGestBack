from flask import request
from flask_restful import Resource
from models.usuario import Usuario
from helpers.database import db, ma
from marshmallow import fields, ValidationError
from sqlalchemy.exc import IntegrityError

# --- Schemas ---
class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True
    
    id = fields.Int(dump_only=True)
    # A senha nunca deve ser retornada na API
    senha_hash = fields.Str(load_only=True, required=True)
    nome = fields.Str(required=True)
    login = fields.Str(required=True)
    perfil = fields.Str(required=True)

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

# --- Resources ---
class UsuarioListResource(Resource):
    def get(self):
        return usuarios_schema.dump(Usuario.query.all())

    def post(self):
        json_data = request.get_json()
        try:
            # TODO: Fazer o hash da senha antes de salvar
            usuario = usuario_schema.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        try:
            db.session.add(usuario)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Login já existe."}, 400
        return usuario_schema.dump(usuario), 201

class UsuarioResource(Resource):
    def get(self, usuario_id):
        return usuario_schema.dump(Usuario.query.get_or_404(usuario_id))

    def delete(self, usuario_id):
        usuario = Usuario.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204

