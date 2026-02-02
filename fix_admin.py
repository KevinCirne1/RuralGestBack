from app import app
from helpers.database import db
from models import Usuario

with app.app_context():
    print("--- Colocando senha em Texto Puro (Para bater com o código) ---")

    # 1. Achar o admin
    admin = Usuario.query.filter_by(login="admin@gmail.com").first()
    
    if admin:
        # 2. AQUI ESTÁ A CORREÇÃO:
        # Atribuímos a string direta, SEM generate_password_hash
        admin.senha = "123456" 
        admin.perfil = "admin"
        
        db.session.commit()
        print("-> SUCESSO! Senha salva como '123456' (texto puro).")
        
    else:
        print("-> Usuário admin não encontrado. Rode o seed_admin antes.")

    print("--------------------------------")
    print("Teste agora com:")
    print("Login: admin@gmail.com")
    print("Senha: 123456")