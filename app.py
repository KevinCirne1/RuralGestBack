from helpers.application import app, api
from helpers.database import db, ma, bcrypt
from helpers.CORS import cors
# Importamos os modelos para garantir que o Migrate os deteta
from models import Agricultor, Propriedade, Usuario, Servico, Solicitacao, Veiculo, Notificacao
# Importamos os comandos (incluindo o novo seed_veiculos)
from commands import seed_admin, reset_db, seed_veiculos
from helpers.migrate import migrate

# Inicialização das extensões
db.init_app(app)
ma.init_app(app)
cors.init_app(app, supports_credentials=True)
bcrypt.init_app(app)
migrate.init_app(app, db)

# Registar os comandos de terminal
app.cli.add_command(seed_admin)
app.cli.add_command(reset_db)
app.cli.add_command(seed_veiculos) # NOVO

# Adicionar os resources (endpoints) à API
from resources.agricultor import AgricultorResource, AgricultorListResource
from resources.propriedade import PropriedadeResource, PropriedadeListResource, AllPropriedadesListResource
from resources.usuario import UsuarioResource, UsuarioListResource
from resources.servico import ServicoResource, ServicoListResource
from resources.solicitacao import SolicitacaoResource, SolicitacaoListResource
from resources.auth import LoginResource
# NOVOS RESOURCES
from resources.veiculo import VeiculoResource, VeiculoListResource
from resources.notificacao import NotificacaoListResource, NotificacaoLerResource

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
# ROTAS NOVAS
api.add_resource(VeiculoListResource, '/veiculos')
api.add_resource(VeiculoResource, '/veiculos/<int:veiculo_id>')
api.add_resource(NotificacaoListResource, '/notificacoes/<int:usuario_id>')
api.add_resource(NotificacaoLerResource, '/notificacoes/ler/<int:notificacao_id>')

if __name__ == '__main__':
    app.run(debug=True)
