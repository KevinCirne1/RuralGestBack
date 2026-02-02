from flask import Flask, jsonify
from flask_migrate import Migrate
import os
from resources.solicitacao import SolicitacaoResource, SolicitacaoListResource
from resources.notificacao import NotificacaoListResource, NotificacaoLerResource
from resources.veiculo import VeiculoListResource, VeiculoResource
# --- CRIAÇÃO DA APP ---
from helpers.application import app, api # Importa a instancia criada no helpers

# --- CONFIGURAÇÃO MANUAL DO BANCO DE DADOS (FORÇA BRUTA) ---
# A senha K123456/ foi convertida para K123456%2F para evitar erros de URL
uri_banco = "postgresql://postgres:K123456%2F@localhost:5432/ruralgest"
app.config['SQLALCHEMY_DATABASE_URI'] = uri_banco
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fh4iuhfiufvihrrtgotr'
# -----------------------------------------------------------

from helpers.database import db, ma
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

# Inicialização das extensões
db.init_app(app)
ma.init_app(app)
cors.init_app(app, supports_credentials=True)

migrate = Migrate(app, db)

# Registar os comandos de terminal
app.cli.add_command(seed_admin)
app.cli.add_command(reset_db)
app.cli.add_command(seed_agricultor) 

# Rotas da API
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
api.add_resource(VeiculoListResource, '/veiculos')
api.add_resource(VeiculoResource, '/veiculos/<int:veiculo_id>')
api.add_resource(LoginResource, '/login')
api.add_resource(NotificacaoListResource, '/notificacoes/<int:usuario_id>')
api.add_resource(NotificacaoLerResource, '/notificacoes/ler/<int:notificacao_id>')

if __name__ == '__main__':
    app.run(debug=True)