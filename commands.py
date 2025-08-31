import click
from flask.cli import with_appcontext
from helpers.database import db
from models.usuario import Usuario
from werkzeug.security import generate_password_hash

@click.command(name='seed_admin')
@with_appcontext
def seed_admin():
    """Cria o primeiro utilizador administrador do sistema."""
    
    login = click.prompt('Digite o login para o administrador')
    
    if Usuario.query.filter_by(login=login).first():
        click.echo('Utilizador com este login já existe.')
        return
        
    nome = click.prompt('Digite o nome do administrador')
    senha = click.prompt('Digite a senha para o administrador', hide_input=True, confirmation_prompt=True)
    
    admin_user = Usuario(
        nome=nome,
        login=login,
        senha_hash=generate_password_hash(senha),
        perfil='gestor' 
    )
    
    db.session.add(admin_user)
    db.session.commit()