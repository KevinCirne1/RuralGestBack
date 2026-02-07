# src/resources/notificacao.py

from flask_restful import Resource, reqparse # Importe o reqparse
from models import Notificacao
from helpers.database import db
from schemas import NotificacaoListaSchema

notificacao_schema = NotificacaoListaSchema(many=True)

# Configura o leitor de parâmetros
parser = reqparse.RequestParser()
parser.add_argument('usuario_id', type=int, location='args', required=True)

class NotificacaoListResource(Resource):
    def get(self): # Remova o usuario_id daqui
        args = parser.parse_args()
        usuario_id = args.get('usuario_id')
        
        notificacoes = Notificacao.query.filter_by(usuario_id=usuario_id)\
            .order_by(Notificacao.lida.asc(), Notificacao.data_criacao.desc())\
            .all()
        return notificacao_schema.dump(notificacoes), 200

class NotificacaoLerResource(Resource):
    # DICA: Mude para POST no seu frontend se preferir, 
    # mas se o service usa PUT, mantenha PUT aqui.
    def post(self, notificacao_id): 
        notificacao = Notificacao.query.get_or_404(notificacao_id)
        notificacao.lida = True
        db.session.commit()
        return {'message': 'Notificação marcada como lida'}, 200