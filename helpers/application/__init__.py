from flask import Flask
from flask_restful import Api
from flask_caching import Cache
from flask_bcrypt import Bcrypt
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
cache = Cache()
bcrypt = Bcrypt(app)
#jwt = JWTManager() 

"""
@jwt.unauthorized_loader
def unauthorized_callback(reason):
    Chamado quando um token é necessário mas não foi fornecido.
    Retorna um JSON informando que é necessário um token de autorização
    com status HTTP 401 (Unauthorized).

@jwt.invalid_token_loader
def invalid_token_callback(error):
    Chamado quando um token inválido é fornecido (ex: assinatura errada).
    Retorna um JSON informando que o token é inválido ou malformado
    com status HTTP 401 (Unauthorized).

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    Chamado quando um token expirado é fornecido.
    Retorna um JSON informando que o token expirou
    com status HTTP 401 (Unauthorized).
"""
