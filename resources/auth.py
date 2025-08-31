from flask import request
from flask_restful import Resource
from models.usuario import Usuario
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

class LoginResource(Resource):
    def post(self):
        json_data = request.get_json()
        login = json_data.get('login')
        senha = json_data.get('senha')

        if not login or not senha:
            return {"message": "Login e senha são obrigatórios"}, 400

        usuario = Usuario.query.filter_by(login=login).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            additional_claims = {"perfil": usuario.perfil}
            access_token = create_access_token(identity=usuario.id, additional_claims=additional_claims)
            
            return {"access_token": access_token}, 200
        
        return {"message": "Credenciais inválidas"}, 401