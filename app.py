from flask_migrate import Migrate
from helpers.application import app, api
from helpers.database import db, ma
from helpers.CORS import cors

# 1. IMPORTAR TODOS OS MODELOS USANDO O __init__.py
# Isso garante que o SQLAlchemy conheça todas as tabelas e relacionamentos
# antes que qualquer outra parte do código (como os resources) tente usá-los.
import models

# 2. AGORA IMPORTAR OS RESOURCES
from resources.agricultor import AgricultorResource, AgricultorListResource
from resources.propriedade import PropriedadeResource, PropriedadeListResource
from resources.usuario import UsuarioResource, UsuarioListResource
from resources.servico import ServicoResource, ServicoListResource
from resources.solicitacao import SolicitacaoResource, SolicitacaoListResource

# Conecta as extensões à aplicação principal
db.init_app(app)
ma.init_app(app)
cors.init_app(app)
migrate = Migrate(app, db)

# Adicionando os resources (endpoints) à API
api.add_resource(AgricultorListResource, '/agricultores')
api.add_resource(AgricultorResource, '/agricultores/<int:agricultor_id>')
api.add_resource(PropriedadeListResource, '/agricultores/<int:agricultor_id>/propriedades')
api.add_resource(PropriedadeResource, '/propriedades/<int:propriedade_id>')
api.add_resource(UsuarioListResource, '/usuarios')
api.add_resource(UsuarioResource, '/usuarios/<int:usuario_id>')
api.add_resource(ServicoListResource, '/servicos')
api.add_resource(ServicoResource, '/servicos/<int:servico_id>')
api.add_resource(SolicitacaoListResource, '/solicitacoes')
api.add_resource(SolicitacaoResource, '/solicitacoes/<int:solicitacao_id>')

if __name__ == '__main__':
    app.run(debug=True)
