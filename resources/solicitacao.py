from datetime import datetime
from flask import request
from flask_restful import Resource
from sqlalchemy import and_
from models import Solicitacao, Notificacao, Usuario, Documento, Propriedade
from helpers.database import db
from marshmallow import ValidationError
from schemas import (
    SolicitacaoDetalhadoSchema,
    SolicitacaoListaSchema,
    SolicitacaoLoadSchema
)

# Inicialização dos Schemas
solicitacao_schema_detalhado = SolicitacaoDetalhadoSchema()
solicitacoes_schema_lista = SolicitacaoListaSchema(many=True)
solicitacao_schema_carga = SolicitacaoLoadSchema()

class SolicitacaoListResource(Resource):
    def get(self):
        operador_id = request.args.get('operador_id')
        agricultor_id = request.args.get('agricultor_id') 
        status = request.args.get('status')
        
        query = Solicitacao.query

        if operador_id:
            query = query.filter_by(operador_id=operador_id)

        if agricultor_id:
            query = query.filter_by(agricultor_id=agricultor_id)
        
        if status:
            query = query.filter_by(status=status)
            
        solicitacoes = query.all()
        return solicitacoes_schema_lista.dump(solicitacoes)

    def post(self):
        json_data = request.get_json()
        
        try:
            # 1. Validação do Marshmallow
            data = solicitacao_schema_carga.load(json_data)
            
            # 2. Validação de Posse: A propriedade pertence ao agricultor?
            propriedade = Propriedade.query.get(data['propriedade_id'])
            if not propriedade:
                return {"message": "A propriedade informada não existe."}, 404

            if str(propriedade.agricultor_id) != str(data['agricultor_id']):
                return {
                    "message": "Erro de Validação",
                    "errors": {"propriedade_id": "Esta propriedade não pertence ao agricultor selecionado."}
                }, 400
            
            # 3. Prevenção de Duplicidade: Já existe pedido aberto para este serviço nesta terra?
            pedido_duplicado = Solicitacao.query.filter(
                and_(
                    Solicitacao.agricultor_id == data['agricultor_id'],
                    Solicitacao.propriedade_id == data['propriedade_id'],
                    Solicitacao.servico_id == data['servico_id'],
                    Solicitacao.status.in_(['Pendente', 'Em Andamento', 'EM ANDAMENTO'])
                )
            ).first()

            if pedido_duplicado:
                return {
                    "message": "Atenção: Você já tem um pedido em aberto para este serviço nesta propriedade.",
                    "id_existente": pedido_duplicado.id
                }, 409

            # 4. Criação
            nova_solicitacao = Solicitacao(data_solicitacao=datetime.now(), **data)
            db.session.add(nova_solicitacao)
            db.session.commit()
            
            # Notificação de Admins
            try:
                admins = Usuario.query.filter(Usuario.perfil.in_(['gestor', 'tecnico'])).all()
                for admin in admins:
                    db.session.add(Notificacao(usuario_id=admin.id, mensagem="Novo Pedido de Serviço Criado"))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Aviso: Erro na notificação: {e}")

            return solicitacao_schema_detalhado.dump(nova_solicitacao), 201

        except ValidationError as err:
            return {"errors": err.messages}, 400
        except Exception as e:
            db.session.rollback()
            print(f"ERRO CRÍTICO: {str(e)}")
            return {"message": "Erro interno", "detalhe": str(e)}, 500

# --- ESTA É A CLASSE QUE ESTAVA FALTANDO E CAUSOU O ERRO NO APP.PY ---
class SolicitacaoResource(Resource):
    def get(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        return solicitacao_schema_detalhado.dump(solicitacao)

    def put(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        
        # --- TRAVA DE SEGURANÇA: Só edita se estiver Pendente ---
        if solicitacao.status.lower() != 'pendente':
            return {
                "message": "Bloqueio de Edição",
                "detalhe": f"Esta solicitação está com status '{solicitacao.status}' e não pode mais ser alterada."
            }, 400
        # -------------------------------------------------------

        json_data = request.get_json()
        try:
            data = solicitacao_schema_carga.load(json_data, partial=True)
            status_antigo = solicitacao.status
            
            # Atualiza os campos
            for key, value in data.items():
                setattr(solicitacao, key, value)
            
            # Automação de Data de Execução
            status_fim = ['Concluída', 'Concluida', 'CONCLUÍDA', 'Finalizada']
            if solicitacao.status in status_fim and 'data_execucao' not in json_data:
                solicitacao.data_execucao = datetime.now()

            # Notifica o agricultor se o status mudar (caso o técnico mude de Pendente para outro)
            if 'status' in data and data['status'] != status_antigo:
                agricultor = solicitacao.agricultor
                if agricultor and agricultor.usuario_id:
                    msg = f"Sua solicitação mudou para: {solicitacao.status}"
                    db.session.add(Notificacao(usuario_id=agricultor.usuario_id, mensagem=msg))

            db.session.commit()
            return solicitacao_schema_detalhado.dump(solicitacao)
            
        except ValidationError as err:
            return {"messages": err.messages}, 400

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        
        # --- TRAVA DE SEGURANÇA: Só deleta se estiver Pendente ---
        if solicitacao.status.lower() != 'pendente':
            return {
                "message": "Não é possível excluir uma solicitação que já foi processada."
            }, 400
        
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204