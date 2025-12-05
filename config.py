import os
#rom datetime import timedelta # Importamos o timedelta para definir o tempo
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Configurações do Redis/Cache ---
    CACHE_TYPE = 'RedisCache' # Usa o Redis como backend de cache
    CACHE_DEFAULT_TIMEOUT = 300 # Tempo de expiração padrão em segundos (5 minutos)
    CACHE_REDIS_HOST = os.environ.get('REDIS_HOST')
    CACHE_REDIS_PORT = os.environ.get('REDIS_PORT')
    # Se o Redis exigir autenticação
    # CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') 
    CACHE_REDIS_URL = f"redis://{CACHE_REDIS_HOST}:{CACHE_REDIS_PORT}/0"
    
    # --- Configurações do JWT --
    #JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    #JWT_TOKEN_LOCATION = ['headers']
    #JWT_HEADER_NAME = 'Authorization'
    #JWT_HEADER_TYPE = 'Bearer'
    
    # AUMENTA O TEMPO DE VIDA DO TOKEN DE ACESSO PARA 1 HORA
    #JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
