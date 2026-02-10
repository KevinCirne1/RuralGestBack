from app import app
from helpers.database import db
from models.veiculo import Veiculo

def cadastrar_veiculos_padrao():
    # Lista de veículos pedidos
    frota_inicial = [
        {"nome": "Caminhão Caçamba 01", "tipo": "Caminhão", "placa": "PM-0001"},
        {"nome": "Retroescavadeira 01", "tipo": "Retroescavadeira", "placa": "PM-0002"},
        {"nome": "Motoniveladora 01", "tipo": "Motoniveladora", "placa": "PM-0003"},
        {"nome": "Pá Mecânica 01", "tipo": "Pá Mecânica", "placa": "PM-0004"},
        {"nome": "Trator com Grade", "tipo": "Trator", "placa": "PM-0005"},
        {"nome": "Trator com Carroção", "tipo": "Trator", "placa": "PM-0006"}
    ]

    with app.app_context():
        print("🚜 Iniciando cadastro da frota...")
        
        adicionados = 0
        for item in frota_inicial:
            # Verifica se já existe um veículo com esse nome para não duplicar
            existe = Veiculo.query.filter_by(nome=item["nome"]).first()
            
            if not existe:
                novo_veiculo = Veiculo(
                    nome=item["nome"],
                    tipo=item["tipo"],
                    placa=item["placa"],
                    status="DISPONIVEL" # Todos começam livres
                )
                db.session.add(novo_veiculo)
                adicionados += 1
                print(f"✅ Adicionado: {item['nome']}")
            else:
                print(f"ℹ️ Já existe: {item['nome']}")
        
        db.session.commit()
        print(f"\n🏁 Concluído! {adicionados} novos veículos cadastrados.")

if __name__ == "__main__":
    cadastrar_veiculos_padrao()