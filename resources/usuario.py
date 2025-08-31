from flask import request
from flask_restful import Resource
from models.usuario import Usuario
from helpers.database import db, ma
from marshmallow import fields, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt

# --- Schemas ---
class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True
    
    id = fields.Int(dump_only=True)
    senha = fields.Str(load_only=True, required=True, data_key="senha")
    nome = fields.Str(required=True)
    login = fields.Str(required=True)
    perfil = fields.Str(required=True)
    solicitacoes_atendidas = fields.Nested("resources.solicitacao.SolicitacaoSchema", many=True, dump_only=True)

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

# --- Resources ---
class UsuarioListResource(Resource):
    @jwt_required() 
    def get(self):
        
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado."}, 403
        return usuarios_schema.dump(Usuario.query.all())

    @jwt_required() 
    def post(self): 
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado. Apenas gestores podem criar novos utilizadores."}, 403

        json_data = request.get_json()
        try:
            senha_plana = json_data.pop('senha', None)
            if not senha_plana:
                 return {"messages": {"senha": ["Senha é obrigatória."]}}, 400

            usuario_data = usuario_schema.load(json_data)
            usuario_data.senha_hash = generate_password_hash(senha_plana)

        except ValidationError as err:
            return {"messages": err.messages}, 400
        try:
            db.session.add(usuario_data)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Login já existe."}, 400
            
        return usuario_schema.dump(usuario_data), 201

class UsuarioResource(Resource):
    @jwt_required()
    def get(self, usuario_id):
        return usuario_schema.dump(Usuario.query.get_or_404(usuario_id))

    @jwt_required()
    def delete(self, usuario_id):
        claims = get_jwt()
        if claims.get('perfil') != 'gestor':
            return {"message": "Acesso negado. Apenas gestores podem executar esta ação."}, 403

        usuario = Usuario.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204