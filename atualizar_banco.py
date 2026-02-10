from app import app
from helpers.database import db
from sqlalchemy import text

def atualizar_banco():
    with app.app_context():
        print("🔄 Iniciando atualização do banco...")
        
        # 1. Garante que a tabela 'veiculo' existe (se não existir, ele cria)
        db.create_all()
        print("✅ Tabelas novas verificadas.")

        # 2. Tenta adicionar a coluna 'veiculo_id' na tabela 'solicitacao' manualmente
        try:
            with db.session.begin():
                # Comando SQL para Postgres
                sql = text("ALTER TABLE solicitacao ADD COLUMN veiculo_id INTEGER REFERENCES veiculo(id);")
                db.session.execute(sql)
            print("✅ Sucesso! Coluna 'veiculo_id' adicionada na tabela 'solicitacao'.")
        except Exception as e:
            # Se der erro, provavelmente é porque a coluna já existe ou outro detalhe, mostramos o erro mas não travamos
            print(f"⚠️ Aviso (Verifique se a coluna já existe): {str(e)}")

if __name__ == "__main__":
    atualizar_banco()