from flask_migrate import Migrate
from helpers.database import db
from helpers.application import app, api, jwt
from helpers.CORS import cors
from models import * 
from commands import seed_admin, reset_db 
import schemas 


db.init_app(app)
jwt.init_app(app)
cors.init_app(app)
migrate = Migrate(app, db) 

# Importação dos resources DEPOIS da inicialização
from resources.agricultor import AgricultorResource, AgricultorListResource
from resources.propriedade import PropriedadeResource, PropriedadeListResource, AllPropriedadesListResource
from resources.usuario import UsuarioResource, UsuarioListResource
from resources.servico import ServicoResource, ServicoListResource
from resources.solicitacao import SolicitacaoResource, SolicitacaoListResource
from resources.auth import LoginResource

# Adicionando os resources (endpoints) à API
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

# Adicionando os comandos de terminal
app.cli.add_command(seed_admin)
app.cli.add_command(reset_db) # Adiciona o novo comando

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)