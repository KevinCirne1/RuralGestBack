
from flask import request
from flask_restful import Resource
from models import Solicitacao
from helpers.database import db
from marshmallow import ValidationError
from schemas import (
    SolicitacaoDetalhadoSchema,
    SolicitacaoListaSchema,
    SolicitacaoLoadSchema
)
from helpers.application import cache

# --- Instâncias dos Schemas ---
solicitacao_schema_detalhado = SolicitacaoDetalhadoSchema()
solicitacoes_schema_lista = SolicitacaoListaSchema(many=True)
solicitacao_schema_carga = SolicitacaoLoadSchema()

# --- Resources ---

class SolicitacaoListResource(Resource):
    @cache.cached(timeout=600, key_prefix='all_solicitacoes')
    def get(self):
        solicitacoes = Solicitacao.query.all()
        return solicitacoes_schema_lista.dump(solicitacoes)

    def post(self):
        json_data = request.get_json()
        try:
            dados_validados = solicitacao_schema_carga.load(json_data)
            nova_solicitacao = Solicitacao(**dados_validados)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        db.session.add(nova_solicitacao)
        db.session.commit()

        cache.delete('all_solicitacoes')
        return solicitacao_schema_detalhado.dump(nova_solicitacao), 201

class SolicitacaoResource(Resource):
    @cache.cached(timeout=600, key_prefix='solicitacao')
    def get(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        return solicitacao_schema_detalhado.dump(solicitacao)

    def put(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        try:
            dados_validados = solicitacao_schema_carga.load(json_data, partial=True)
            for key, value in dados_validados.items():
                setattr(solicitacao, key, value)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        db.session.commit()

        cache.delete('all_solicitacoes')
        cache.delete(f'solicitacao_{solicitacao_id}')
        return solicitacao_schema_detalhado.dump(solicitacao)

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        db.session.delete(solicitacao)
        db.session.commit()
        cache.delete('all_solicitacoes')
        cache.delete(f'solicitacao_{solicitacao_id}')
        return '', 204