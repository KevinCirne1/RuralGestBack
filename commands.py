# ==============================================================================
from flask.cli import with_appcontext
import click
from werkzeug.security import generate_password_hash
from models import Usuario, Agricultor, Propriedade, Servico, Solicitacao
from helpers.database import db
from sqlalchemy import text # <-- ADICIONADO: Importa a função text

@click.command('seed_admin')
@with_appcontext
def seed_admin():
    """Cria o utilizador administrador inicial."""
    try:
        login = click.prompt('Digite o login para o administrador', type=str)
        nome = click.prompt('Digite o nome do administrador', type=str)
        senha = click.prompt('Digite a senha para o administrador', type=str, hide_input=True, confirmation_prompt=True)
        
        if Usuario.query.filter_by(login=login).first():
            click.echo('Utilizador com este login já existe.')
            return

        novo_admin = Usuario(
            nome=nome,
            login=login,
            senha_hash=generate_password_hash(senha),
            perfil='gestor'
        )

        db.session.add(novo_admin)
        db.session.commit()
        click.echo(f'Utilizador administrador "{nome}" criado com sucesso!')

    except Exception as e:
        db.session.rollback()
        click.echo(f'Erro ao criar administrador: {e}')

@click.command('reset_db')
@with_appcontext
def reset_db():
    """Apaga todos os dados das tabelas e reinicia os contadores de ID."""
    if click.confirm('Tem a certeza que quer apagar TODOS os dados da base de dados? Esta ação é irreversível.', abort=True):
        try:
            # Apaga os dados na ordem correta para evitar erros de chave estrangeira
            db.session.query(Solicitacao).delete()
            db.session.query(Propriedade).delete()
            db.session.query(Servico).delete()
            db.session.query(Agricultor).delete()
            db.session.query(Usuario).delete()
            
            db.session.commit()
            
            # Reinicia os contadores de ID (específico para PostgreSQL)
            # CORREÇÃO: Envolvemos a string SQL com a função text()
            db.session.execute(text('TRUNCATE TABLE solicitacao, propriedade, servico, agricultor, usuario RESTART IDENTITY;'))
            db.session.commit()
            
            click.echo('Base de dados zerada com sucesso!')
        except Exception as e:
            db.session.rollback()
            click.echo(f'Erro ao zerar a base de dados: {e}')
            