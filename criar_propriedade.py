from app import app
from helpers.database import db
from models import Agricultor, Propriedade, Usuario

with app.app_context():
    print("--- Finalizando Cadastro da Propriedade ---")

    # 1. Achar o Login do José
    usuario_jose = Usuario.query.filter(Usuario.login.like('%agricultor%')).first()
    
    if not usuario_jose:
        print("ERRO: Usuário não encontrado. Crie o usuário primeiro.")
        exit()

    print(f"-> Usuário encontrado: {usuario_jose.login}")

    # 2. Achar o Perfil de Agricultor (que criamos no passo anterior)
    agricultor = Agricultor.query.filter_by(usuario_id=usuario_jose.id).first()

    if not agricultor:
        # Caso tenha dado erro antes de salvar o agricultor, criamos agora
        print("-> Criando perfil de Agricultor...")
        agricultor = Agricultor(
            nome="José Agricultor",
            cpf="123.456.789-00",
            comunidade="Comunidade Rural 1",
            contato="83999999999",
            usuario_id=usuario_jose.id
        )
        db.session.add(agricultor)
        db.session.commit() # Salva para gerar o ID
    else:
        print("-> Perfil de Agricultor já existente e carregado.")

    # 3. Criar a Propriedade (Agora com os campos CERTOS)
    # Verifica se já existe pelo nome do 'terreno'
    prop_existente = Propriedade.query.filter_by(terreno="Sítio Esperança").first()

    if not prop_existente:
        prop = Propriedade(
            terreno="Sítio Esperança",              # Antigo 'nome'
            tipo_agricultura="Familiar Mista",      # Novo campo obrigatório
            area_total=15.5,                        # Antigo 'tamanho_hectares'
            area_exploravel=10.0,                   # Novo campo obrigatório
            coordenadas_geograficas="-6.123, -35.456", # Novo campo obrigatório
            agricultor_id=agricultor.id
        )
        db.session.add(prop)
        db.session.commit()
        print("-> SUCESSO! Propriedade 'Sítio Esperança' criada!")
    else:
        print("-> A propriedade 'Sítio Esperança' já existe.")

    print("--- CONFIGURAÇÃO CONCLUÍDA ---")