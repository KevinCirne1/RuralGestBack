import click
from helpers.database import db
from models import Usuario, Veiculo
from sqlalchemy import text

@click.command('seed_admin')
def seed_admin():
    try:
        login = click.prompt('Digite o login para o administrador', type=str)
        nome = click.prompt('Digite o nome do administrador', type=str)
        senha = click.prompt('Digite a senha para o administrador', type=str, hide_input=True, confirmation_prompt=True)
        
        if Usuario.query.filter_by(login=login).first():
            click.echo('Erro: O utilizador administrador com este login já existe.')
            return

        admin = Usuario(nome=nome, login=login, senha=senha, perfil='gestor')
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Utilizador administrador "{nome}" criado com sucesso!')

    except Exception as e:
        click.echo(f"Erro ao criar o administrador: {e}")

@click.command('reset_db')
def reset_db():
    if click.confirm('Tem a certeza que quer apagar TODOS os dados?'):
        try:
            db.session.execute(text('TRUNCATE TABLE notificacao, solicitacao, veiculo, servico, propriedade, agricultor, usuario RESTART IDENTITY CASCADE;'))
            db.session.commit()
            click.echo('Todos os dados foram apagados.')
        except Exception as e:
            db.session.rollback()
            click.echo(f"Erro ao zerar a base de dados: {e}")

# NOVO COMANDO
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
