from flask import Flask
from flask_restful import Api
from config import Config
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
jwt = JWTManager()