from flask import Flask
from flask_restful import Api
from config import Config
from helpers.database import db, ma, bcrypt
from flask_caching import Cache # <--- Importar
import os

app = Flask(__name__)
app.config.from_object(Config)

# Configuração do Redis (Pega do .env ou usa padrão local)
# Se estiver rodando no docker-compose, o host será 'redis'
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)

# Configura o Cache
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300, # 5 minutos padrão
    "CACHE_REDIS_HOST": redis_host,
    "CACHE_REDIS_PORT": redis_port
}

# Inicializa extensões
db.init_app(app)
ma.init_app(app)
bcrypt.init_app(app)
cache = Cache(app, config=cache_config) # <--- Inicializa o Cache

api = Api(app)