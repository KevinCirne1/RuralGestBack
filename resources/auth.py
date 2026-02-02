from flask import request
from flask_restful import Resource
from models.usuario import Usuario
from schemas import UsuarioDetalhadoSchema

# Instância do schema para este resource
usuario_schema_detalhado = UsuarioDetalhadoSchema()

class LoginResource(Resource):
    def post(self):
        json_data = request.get_json()
        login = json_data.get('login')
        senha = json_data.get('senha')

        if not login or not senha:
            return {"message": "Login e senha são obrigatórios"}, 400

        utilizador = Usuario.query.filter_by(login=login).first()

        if utilizador and utilizador.verificar_senha(senha):
            return usuario_schema_detalhado.dump(utilizador), 200
        
        return {"message": "Credenciais inválidas"}, 401
