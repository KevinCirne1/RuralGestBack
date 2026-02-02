from flask_restful import Resource
from models import Notificacao
from helpers.database import db
from flask import jsonify

class NotificacaoListResource(Resource):
    def get(self, usuario_id):
        # Busca notificações do usuário (Não lidas primeiro)
        notificacoes = Notificacao.query.filter_by(usuario_id=usuario_id)\
            .order_by(Notificacao.lida.asc(), Notificacao.data_criacao.desc())\
            .all()
        return [n.to_json() for n in notificacoes], 200

class NotificacaoLerResource(Resource):
    def put(self, notificacao_id):
        # Marca uma notificação específica como lida
        notificacao = Notificacao.query.get(notificacao_id)
        if notificacao:
            notificacao.lida = True
            db.session.commit()
            return {'message': 'Notificação marcada como lida'}, 200
        return {'message': 'Notificação não encontrada'}, 404