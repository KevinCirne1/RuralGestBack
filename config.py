import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações explícitas para o JWT
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization' # <-- LINHA ADICIONADA
    JWT_HEADER_TYPE = 'Bearer'