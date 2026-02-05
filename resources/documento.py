from flask import request
from flask_restful import Resource
from models import Documento, Solicitacao
from helpers.database import db
from marshmallow import ValidationError
from schemas import DocumentoListaSchema, DocumentoLoadSchema

# --- Instâncias dos Schemas
documento_schema_carga = DocumentoLoadSchema()
documentos_schema_lista = DocumentoListaSchema(many=True)
documento_schema_detalhado = DocumentoListaSchema() 

class DocumentoListResource(Resource):
    def get(self):
        # Lista documentos. Pode filtrar por solicitação.
        solicitacao_id = request.args.get('solicitacao_id')
        if solicitacao_id:
            documentos = Documento.query.filter_by(solicitacao_id=solicitacao_id).all()
        else:
            documentos = Documento.query.all()
        return documentos_schema_lista.dump(documentos)

    def post(self):
        # Gera/Regista um novo documento
        json_data = request.get_json()
        try:
            data = documento_schema_carga.load(json_data)
            
            # Verifica se a solicitação existe
            solicitacao = Solicitacao.query.get_or_404(data['solicitacao_id'])
            
            # Cria o registo do documento
            novo_doc = Documento(
                solicitacao_id=data['solicitacao_id'],
                tipo_documento=data['tipo_documento']
            )
            
            db.session.add(novo_doc)
            db.session.commit()
            
            # NOTA: Num sistema real, aqui chamaríamos uma função para gerar o PDF
            # e salvaríamos o ficheiro no disco. Para o TCC, registar os metadados
            # e devolver a "assinatura digital" simulada já cumpre o requisito de banco de dados.
            
            return documento_schema_detalhado.dump(novo_doc), 201
            
        except ValidationError as err:
            return {"messages": err.messages}, 400

class DocumentoResource(Resource):
    def get(self, documento_id):
        doc = Documento.query.get_or_404(documento_id)
        return documento_schema_detalhado.dump(doc)
    
    def delete(self, documento_id):
        doc = Documento.query.get_or_404(documento_id)
        db.session.delete(doc)
        db.session.commit()
        return '', 204