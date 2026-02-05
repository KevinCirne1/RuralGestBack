from flask import request
from flask_restful import Resource
from models import Solicitacao, Notificacao, Usuario, Documento
from helpers.database import db
from marshmallow import ValidationError
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
            data = solicitacao_schema_carga.load(json_data)
            nova_solicitacao = Solicitacao(**data)
            db.session.add(nova_solicitacao)
            db.session.commit()
            
            # Notifica Admins (Lógica do seu amigo)
            try:
                admins = Usuario.query.filter(Usuario.perfil.in_(['gestor', 'tecnico'])).all()
                if admins:
                    msg = "Novo Pedido: Uma solicitação foi criada."
                    for admin in admins:
                        db.session.add(Notificacao(usuario_id=admin.id, mensagem=msg))
                    db.session.commit()
            except Exception as e:
                print(f"❌ Erro ao notificar admins: {e}")

            return solicitacao_schema_detalhado.dump(nova_solicitacao), 201
        except ValidationError as err:
            return {"messages": err.messages}, 400

class SolicitacaoResource(Resource):
    def get(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        return solicitacao_schema_detalhado.dump(solicitacao)

    def put(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        json_data = request.get_json()
        
        try:
            data = solicitacao_schema_carga.load(json_data, partial=True)
            
            # LÓGICA DE VEÍCULO E NOTIFICAÇÃO
            novo_status = data.get('status')
            
            for key, value in data.items():
                setattr(solicitacao, key, value)
            
            if novo_status == 'APROVADA' and solicitacao.veiculo:
                solicitacao.veiculo.status = 'EM_USO'
            elif novo_status in ['CONCLUÍDA', 'RECUSADA', 'CANCELADA'] and solicitacao.veiculo:
                solicitacao.veiculo.status = 'DISPONIVEL'
            
            db.session.commit()

    # --- 3. GERAÇÃO AUTOMÁTICA: RELATÓRIO FINAL ---
            # Se o serviço for CONCLUÍDO, geramos o documento para assinatura
            if novo_status == 'CONCLUÍDA':
                # Verifica se já não existe para não duplicar
                existe = False
                for doc in solicitacao.documentos:
                    if doc.tipo_documento == "RELATORIO_FINAL":
                        existe = True
                        break
                
                if not existe:
                    relatorio = Documento(
                        solicitacao_id=solicitacao.id,
                        tipo_documento="RELATORIO_FINAL"
                    )
                    relatorio.arquivo_pdf = f"relatorio_final_{solicitacao.id}.pdf"
                    db.session.add(relatorio)

            # Notifica Agricultor
            if novo_status in ['APROVADA', 'RECUSADA', 'CONCLUÍDA']:
                try:
                    agricultor = solicitacao.agricultor
                    if agricultor and agricultor.usuario_id:
                        msg = f"Sua solicitação foi {novo_status}."
                        if novo_status == 'RECUSADA' and solicitacao.motivo_recusa:
                            msg += f" Motivo: {solicitacao.motivo_recusa}"
                        db.session.add(Notificacao(usuario_id=agricultor.usuario_id, mensagem=msg))
                        db.session.commit()
                except Exception as e:
                    print(f"Erro ao criar notificação: {e}")

            return solicitacao_schema_detalhado.dump(solicitacao)

        except ValidationError as err:
            return {"messages": err.messages}, 400

    def delete(self, solicitacao_id):
        solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
        
        if solicitacao.veiculo and solicitacao.status == 'APROVADA':
            solicitacao.veiculo.status = 'DISPONIVEL'
            
        db.session.delete(solicitacao)
        db.session.commit()
        return '', 204