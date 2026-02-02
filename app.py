from flask import Flask,jsonify
from flask_migrate import Migrate
#from flask_jwt_extended import JWTManager # Importamos o JWTManager diretamente
from helpers.database import db, ma
from helpers.application import app, api
from helpers.cors import cors
from models import Agricultor, Propriedade, Usuario, Servico, Solicitacao
from commands import seed_admin, reset_db, seed_agricultor

# Adicionando os endpoints à API
from resources.agricultor import AgricultorResource, AgricultorListResource
from resources.propriedade import PropriedadeResource, PropriedadeListResource, AllPropriedadesListResource
from resources.usuario import UsuarioResource, UsuarioListResource
from resources.servico import ServicoResource, ServicoListResource
from resources.solicitacao import SolicitacaoResource, SolicitacaoListResource
from resources.auth import LoginResource




# Inicialização das outras extensões

db.init_app(app)
ma.init_app(app)
cors.init_app(app, supports_credentials=True)

migrate = Migrate(app, db)

# Registar os comandos de terminal
app.cli.add_command(seed_admin)
app.cli.add_command(reset_db)


# Adicionar os endpoints à API
from resources.agricultor import AgricultorResource, AgricultorListResource
from resources.propriedade import PropriedadeResource, PropriedadeListResource, AllPropriedadesListResource
from resources.usuario import UsuarioResource, UsuarioListResource
from resources.servico import ServicoResource, ServicoListResource
from resources.solicitacao import SolicitacaoResource, SolicitacaoListResource

api.add_resource(AgricultorListResource, '/agricultores')
api.add_resource(AgricultorResource, '/agricultores/<int:agricultor_id>')
api.add_resource(PropriedadeListResource, '/agricultores/<int:agricultor_id>/propriedades')
api.add_resource(PropriedadeResource, '/propriedades/<int:propriedade_id>')
api.add_resource(AllPropriedadesListResource, '/propriedades')
api.add_resource(UsuarioListResource, '/usuarios')
api.add_resource(UsuarioResource, '/usuarios/<int:usuario_id>')
api.add_resource(ServicoListResource, '/servicos')
api.add_resource(ServicoResource, '/servicos/<int:servico_id>')
api.add_resource(SolicitacaoListResource, '/solicitacoes')
api.add_resource(SolicitacaoResource, '/solicitacoes/<int:solicitacao_id>')
api.add_resource(LoginResource, '/login')

if __name__ == '__main__':
    app.run(debug=True)