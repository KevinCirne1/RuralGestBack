from flask import request, send_file
from flask_restful import Resource
from models import Documento, Solicitacao
from helpers.database import db
from marshmallow import ValidationError
from schemas import DocumentoListaSchema, DocumentoLoadSchema
import os

# --- Instâncias dos Schemas 
documento_schema_carga = DocumentoLoadSchema()
documentos_schema_lista = DocumentoListaSchema(many=True)
documento_schema_detalhado = DocumentoListaSchema() 

class DocumentoListResource(Resource):
    def get(self):
        # Lista documentos. Pode filtrar por solicitação: ?solicitacao_id=X
        solicitacao_id = request.args.get('solicitacao_id')
        if solicitacao_id:
            documentos = Documento.query.filter_by(solicitacao_id=solicitacao_id).all()
        else:
            documentos = Documento.query.all()
        return documentos_schema_lista.dump(documentos)

    def post(self):
        # Registo manual de documento (raramente usado agora com a automação)
        json_data = request.get_json()
        try:
            data = documento_schema_carga.load(json_data)
            Solicitacao.query.get_or_404(data['solicitacao_id'])
            
            novo_doc = Documento(
                solicitacao_id=data['solicitacao_id'],
                tipo_documento=data['tipo_documento']
            )
            
            db.session.add(novo_doc)
            db.session.commit()
            return documento_schema_detalhado.dump(novo_doc), 201
        except ValidationError as err:
            return {"messages": err.messages}, 400

class DocumentoResource(Resource):
    def get(self, documento_id):
        doc = Documento.query.get_or_404(documento_id)
        return documento_schema_detalhado.dump(doc)
    
    def delete(self, documento_id):
        doc = Documento.query.get_or_404(documento_id)
        # Opcional: Remover ficheiro físico ao apagar da DB
        pasta = os.path.abspath("documentos_gerados")
        caminho = os.path.join(pasta, doc.arquivo_pdf)
        if os.path.exists(caminho):
            os.remove(caminho)
            
        db.session.delete(doc)
        db.session.commit()
        return '', 204

# --- ENDPOINT PARA DOWNLOAD REAL ---
class DocumentoDownloadResource(Resource):
    def get(self, documento_id):
        """
        Garante o envio do ficheiro PDF binário para o navegador.
        Caminho sugerido: GET /documentos/download/<int:documento_id>
        """
        doc = Documento.query.get_or_404(documento_id)
        
        # Caminho absoluto da pasta de armazenamento
        base_dir = os.path.abspath("documentos_gerados")
        file_path = os.path.join(base_dir, doc.arquivo_pdf)
        
        if not os.path.exists(file_path):
            return {"message": "O ficheiro PDF não foi encontrado no servidor físico."}, 404
            
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=doc.arquivo_pdf
        )