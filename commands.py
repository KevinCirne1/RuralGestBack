import click
from models.usuario import Usuario
from helpers.database import db

@click.command('seed_admin')
def seed_admin():
    """Cria o utilizador administrador inicial."""
    try:
        login = click.prompt('Digite o login para o administrador', type=str)
        nome = click.prompt('Digite o nome do administrador', type=str)
        senha = click.prompt('Digite a senha para o administrador', type=str, hide_input=True, confirmation_prompt=True)
        
        if Usuario.query.filter_by(login=login).first():
            click.echo('Erro: O utilizador administrador com este login já existe.')
            return

        # Agora cria o utilizador com a senha em texto simples
        admin = Usuario(nome=nome, login=login, senha=senha, perfil='gestor')
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Utilizador administrador "{nome}" criado com sucesso!')

    except Exception as e:
        click.echo(f"Erro ao criar o administrador: {e}")

@click.command('reset_db')
def reset_db():
    """Apaga todos os dados de todas as tabelas."""
    if click.confirm('Tem a certeza que quer apagar TODOS os dados da base de dados? Esta ação é irreversível.'):
        try:
            # Apaga os dados em ordem de dependência para evitar erros
            db.session.execute(db.text('TRUNCATE TABLE solicitacao, servico, usuario, propriedade, agricultor RESTART IDENTITY CASCADE;'))
            db.session.commit()
            click.echo('Todos os dados foram apagados e os contadores de ID reiniciados.')
        except Exception as e:
            db.session.rollback()
            click.echo(f"Erro ao zerar a base de dados: {e}")