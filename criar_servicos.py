from app import app
from helpers.database import db
from models import Servico

# Este script roda fora do terminal interativo, então não tem erro de espaço!
with app.app_context():
    print("--- Iniciando Cadastro de Serviços ---")

    # 1. Cria Corte de Terra
    if not Servico.query.filter_by(nome_servico="Corte de Terra").first():
        s1 = Servico(
            nome_servico="Corte de Terra", 
            descricao="Trator para arar a terra", 
            capacidade_hectares=10.0
        )
        db.session.add(s1)
        print("-> Serviço 'Corte de Terra' preparado.")
    else:
        print("-> 'Corte de Terra' já existe.")

    # 2. Cria Gradeamento
    if not Servico.query.filter_by(nome_servico="Gradeamento").first():
        s2 = Servico(
            nome_servico="Gradeamento", 
            descricao="Preparação de solo para plantio", 
            capacidade_hectares=15.0
        )
        db.session.add(s2)
        print("-> Serviço 'Gradeamento' preparado.")
    else:
        print("-> 'Gradeamento' já existe.")
        
    # Salva tudo no banco de verdade
    db.session.commit()
    print("--- SUCESSO! Serviços salvos no banco de dados. ---")