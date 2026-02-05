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
# Importamos o gerador
from helpers.pdf.gerador_pdf import gerar_pdf_solicitacao

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
            db.session.flush() # Gera o ID

            # --- GERAÇÃO DE PDF (Protocolo) ---
            nome_arquivo = f"protocolo_{nova_solicitacao.id}.pdf"
            # Esta função cria o arquivo na pasta 'documentos_gerados'
            gerar_pdf_solicitacao(nova_solicitacao, "PROTOCOLO", nome_arquivo)

            # Salva no banco
            protocolo = Documento(
                solicitacao_id=nova_solicitacao.id,
                tipo_documento="PROTOCOLO"
            )
            protocolo.arquivo_pdf = nome_arquivo # Guardamos o nome para download
            db.session.add(protocolo)

            # Notifica Admins
            try:
                admins = Usuario.query.filter(Usuario.perfil.in_(['gestor', 'tecnico'])).all()
                msg = "Novo Pedido: Uma solicitação foi criada."
                for admin in admins:
                    db.session.add(Notificacao(usuario_id=admin.id, mensagem=msg))
            except Exception as e:
                print(f"❌ Erro ao notificar admins: {e}")

            db.session.commit()
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
            # LÓGICA DE VEÍCULO E NOTIFICAÇÃO


            data = solicitacao_schema_carga.load(json_data, partial=True)
            novo_status = data.get('status')
            
            for key, value in data.items():
                setattr(solicitacao, key, value)
            
            # Lógica de Veículo
            if novo_status == 'APROVADA' and solicitacao.veiculo:
                solicitacao.veiculo.status = 'EM_USO'
            elif novo_status in ['CONCLUÍDA', 'RECUSADA', 'CANCELADA'] and solicitacao.veiculo:
                solicitacao.veiculo.status = 'DISPONIVEL'
            
            # --- GERAÇÃO DE PDF (Relatório Final) ---
            if novo_status == 'CONCLUÍDA':
            # Verifica se já não existe para não duplicar

                existe = False
                for doc in solicitacao.documentos:
                    if doc.tipo_documento == "RELATORIO_FINAL":
                        existe = True
                        break
                
                if not existe:
                    nome_arquivo = f"relatorio_final_{solicitacao.id}.pdf"
                    gerar_pdf_solicitacao(solicitacao, "RELATORIO_FINAL", nome_arquivo)
                    
                    relatorio = Documento(
                        solicitacao_id=solicitacao.id,
                        tipo_documento="RELATORIO_FINAL"
                    )
                    relatorio.arquivo_pdf = nome_arquivo
                    db.session.add(relatorio)

            db.session.commit()

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
                    print(f"Erro notificação agricultor: {e}")

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