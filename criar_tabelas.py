# criar_tabelas.py
from app import app  # Importe sua aplicação principal
from helpers.database import db # Onde fica sua configuração de banco
from models.notificacao import Notificacao # Importante importar para o SQLAlchemy "ver" a tabela nova

# Força a aplicação a entrar no contexto para acessar o banco
with app.app_context():
    db.create_all()
    print("✅ Sucesso! Tabela 'notificacao' criada (se ela não existia).")