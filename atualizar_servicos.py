from app import app
from helpers.database import db
from sqlalchemy import text

def atualizar_tabela_servicos():
    with app.app_context():
        print("🔄 Atualizando tabela de Serviços...")
        try:
            with db.session.begin():
                # Adiciona a coluna tipo_veiculo na tabela servico
                sql = text("ALTER TABLE servico ADD COLUMN tipo_veiculo VARCHAR(50);")
                db.session.execute(sql)
            print("✅ Sucesso! Coluna 'tipo_veiculo' criada.")
        except Exception as e:
            print(f"⚠️ Aviso (Talvez a coluna já exista): {str(e)}")

if __name__ == "__main__":
    atualizar_tabela_servicos()