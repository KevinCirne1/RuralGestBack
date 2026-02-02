from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from helpers.database import db
from models import Solicitacao, Notificacao, Usuario, Veiculo
from schemas import (
    SolicitacaoDetalhadoSchema,
    SolicitacaoListaSchema,
    SolicitacaoLoadSchema
)

solicitacao_schema_detalhado = SolicitacaoDetalhadoSchema()
solicitacoes_schema_lista = SolicitacaoListaSchema(many=True)
solicitacao_schema_carga = SolicitacaoLoadSchema()

class SolicitacaoListResource(Resource):
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

        # Notifica Admins
        try:
            admins = Usuario.query.filter(Usuario.perfil.in_(['admin', 'tecnico'])).all()
            if admins:
                nome_agricultor = nova_solicitacao.agricultor.nome if nova_solicitacao.agricultor else "Um produtor"
                nome_servico = nova_solicitacao.servico.nome_servico if nova_solicitacao.servico else "um serviço"
                msg = f"Novo Pedido: {nome_agricultor} solicitou {nome_servico}."
                for admin in admins:
                    db.session.add(Notificacao(usuario_id=admin.id, mensagem=msg))
                db.session.commit()
        except Exception as e:
            print(f"❌ Erro ao notificar admins: {e}")

        return solicitacao_schema_detalhado.dump(nova_solicitacao), 201

class SolicitacaoResource(Resource):
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
            
            # --- TRAVA/DESTRAVA VEÍCULO ---
            novo_status = dados_validados.get('status')
            if novo_status == 'APROVADA' and solicitacao.veiculo:
                solicitacao.veiculo.status = 'EM_USO'
            elif novo_status in ['CONCLUÍDA', 'RECUSADA', 'CANCELADA'] and solicitacao.veiculo:
                solicitacao.veiculo.status = 'DISPONIVEL'

        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.commit()

        # --- NOTIFICAÇÃO INTELIGENTE (COM MOTIVO) ---
        if novo_status in ['APROVADA', 'RECUSADA', 'CONCLUÍDA']:
            try:
                agricultor = solicitacao.agricultor
                if agricultor and agricultor.usuario_id:
                    nome_servico = solicitacao.servico.nome_servico if solicitacao.servico else "Serviço"
                    
                    # Monta a mensagem base
                    msg = f"Sua solicitação para {nome_servico} foi {novo_status}."
                    
                    # SE FOI RECUSADA, ADICIONA O MOTIVO NA MENSAGEM
                    if novo_status == 'RECUSADA' and solicitacao.motivo_recusa:
                        msg += f" Motivo: {solicitacao.motivo_recusa}"
                    
                    db.session.add(Notificacao(usuario_id=agricultor.usuario_id, mensagem=msg))
                    db.session.commit()
            except Exception as e:
                print(f"❌ Erro ao notificar agricultor: {e}")

        return solicitacao_schema_detalhado.dump(solicitacao)

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        if solicitacao.veiculo and solicitacao.status == 'APROVADA':
             solicitacao.veiculo.status = 'DISPONIVEL'
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204