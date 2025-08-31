from flask import Flask, jsonify
from flask_restful import Api
from config import Config
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
jwt = JWTManager()

# --- CORREÇÃO: Gestores de Erro Personalizados para o JWT ---
# Estas funções garantem que a API devolve o código de erro 401 (Não Autorizado)
# em vez do 422, que era confuso.

@jwt.unauthorized_loader
def unauthorized_callback(reason):
    """Chamado quando um token é necessário mas não foi fornecido."""
    return jsonify({"msg": "É necessário um token de autorização."}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Chamado quando um token inválido é fornecido (ex: assinatura errada)."""
    return jsonify({"msg": "Token inválido ou malformado."}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Chamado quando um token expirado é fornecido."""
    return jsonify({"msg": "O seu token expirou."}), 401