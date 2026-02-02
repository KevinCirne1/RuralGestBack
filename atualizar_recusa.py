from app import app
from helpers.database import db
from sqlalchemy import text

def atualizar_tabela_solicitacao():
    with app.app_context():
        print("🔄 Adicionando coluna 'motivo_recusa'...")
        try:
            with db.session.begin():
                # Cria a coluna de texto para a justificativa
                sql = text("ALTER TABLE solicitacao ADD COLUMN motivo_recusa VARCHAR(255);")
                db.session.execute(sql)
            print("✅ Sucesso! Agora podemos salvar o motivo.")
        except Exception as e:
            print(f"⚠️ Aviso (Talvez já exista): {str(e)}")

if __name__ == "__main__":
    atualizar_tabela_solicitacao()