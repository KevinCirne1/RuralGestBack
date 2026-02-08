import click
from models.usuario import Usuario
from models.veiculo import Veiculo
from models.agricultor import Agricultor
from helpers.database import db
from sqlalchemy import text

@click.command('seed_admin')
def seed_admin():
    """Cria o utilizador administrador inicial."""
    try:
        login = click.prompt('Digite o login para o administrador', type=str)
        nome = click.prompt('Digite o nome do administrador', type=str)
        senha = click.prompt('Digite a senha para o administrador', type=str, hide_input=True, confirmation_prompt=True)
        
        if Usuario.query.filter_by(login=login).first():
            click.echo('Erro: O utilizador com este login já existe.')
            return

        # Cria o admin com perfil 'gestor'
        admin = Usuario(nome=nome, login=login, senha=senha, perfil='gestor')
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Administrador "{nome}" criado com sucesso!')

    except Exception as e:
        click.echo(f"Erro ao criar o administrador: {e}")

@click.command('seed_agricultor')
def seed_agricultor():
    """Cria um agricultor completo (Usuário + Dados Pessoais) para testes."""
    try:
        # 1. Dados de Acesso (Usuario)
        click.echo("\n--- Dados de Acesso ---")
        login = click.prompt('Login (Email/CPF)', type=str)
        senha = click.prompt('Senha', type=str, hide_input=True, confirmation_prompt=True)
        
        if Usuario.query.filter_by(login=login).first():
            click.echo('Erro: Já existe um usuário com este login.')
            return

        # 2. Dados Pessoais (Agricultor)
        click.echo("\n--- Dados Pessoais ---")
        nome = click.prompt('Nome Completo', type=str)
        cpf = click.prompt('CPF', type=str)
        comunidade = click.prompt('Comunidade', type=str)
        contato = click.prompt('Contato (Tel)', type=str, default="00 0000-0000")

        if Agricultor.query.filter_by(cpf=cpf).first():
            click.echo('Erro: Já existe um agricultor com este CPF.')
            return

        # 3. Criação no Banco (Transação Única)
        
        # Passo A: Cria o Usuário
        novo_usuario = Usuario(nome=nome, login=login, senha=senha, perfil='agricultor')
        db.session.add(novo_usuario)
        db.session.flush() # Gera o ID do usuário sem fechar a transação

        # Passo B: Cria o Agricultor vinculado ao Usuário
        novo_agricultor = Agricultor(
            nome=nome,
            cpf=cpf,
            comunidade=comunidade,
            contato=contato,
            usuario_id=novo_usuario.id # <--- O VÍNCULO MÁGICO
        )
        db.session.add(novo_agricultor)

        # Passo C: Salva tudo
        db.session.commit()
        
        click.echo(f'\nSUCESSO: Agricultor "{nome}" cadastrado!')
        click.echo(f' -> ID Usuário: {novo_usuario.id}')
        click.echo(f' -> ID Agricultor: {novo_agricultor.id}')

    except Exception as e:
        db.session.rollback()
        click.echo(f"Erro ao criar o agricultor: {e}")

@click.command('reset_db')
def reset_db():
    """Apaga todos os dados de todas as tabelas."""
    if click.confirm('Tem a certeza que quer apagar TODOS os dados da base de dados? Esta ação é irreversível.'):
        try:
            # Apaga os dados em ordem de dependência para evitar erros de chave estrangeira
            db.session.execute(text('TRUNCATE TABLE solicitacao, servico, usuario, propriedade, agricultor RESTART IDENTITY CASCADE;'))
            db.session.commit()
            click.echo('Todos os dados foram apagados e os contadores de ID reiniciados.')
        except Exception as e:
            db.session.rollback()
            click.echo(f"Erro ao zerar a base de dados: {e}")

@click.command('seed_veiculos')
def seed_veiculos():
    """Cadastra a frota inicial de veículos."""
    frota = [
        {"nome": "Caminhão Caçamba 01", "tipo": "Caminhão", "placa": "PM-0001"},
        {"nome": "Retroescavadeira 01", "tipo": "Retroescavadeira", "placa": "PM-0002"},
        {"nome": "Motoniveladora 01", "tipo": "Motoniveladora", "placa": "PM-0003"},
        {"nome": "Trator com Grade", "tipo": "Trator", "placa": "PM-0005"},
    ]
    try:
        count = 0
        for v in frota:
            if not Veiculo.query.filter_by(nome=v["nome"]).first():
                novo = Veiculo(nome=v["nome"], tipo=v["tipo"], placa=v["placa"], status="DISPONIVEL")
                db.session.add(novo)
                count += 1
        db.session.commit()
        click.echo(f"Sucesso! {count} veículos adicionados.")
    except Exception as e:
        click.echo(f"Erro: {e}")