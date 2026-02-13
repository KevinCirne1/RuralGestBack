from flask import request
from flask_restful import Resource
from models import Agricultor, Usuario  
from helpers.database import db
from marshmallow import ValidationError

# REMOVIDO: from werkzeug.security ... (O Model Usuario já faz isso!)

from schemas import (
    AgricultorDetalhadoSchema, 
    AgricultorListaSchema, 
    AgricultorLoadSchema
)

# Instâncias dos Schemas
agricultor_schema_detalhado = AgricultorDetalhadoSchema()
agricultores_schema_lista = AgricultorListaSchema(many=True)
agricultor_schema_carga = AgricultorLoadSchema()

class AgricultorListResource(Resource):
    def get(self):
        agricultores = Agricultor.query.all()
        return agricultores_schema_lista.dump(agricultores)

    def post(self):
        json_data = request.get_json()
        
        # 1. Valida os dados do Agricultor
        try:
            dados_validados = agricultor_schema_carga.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400

        try:
            # 2. Dados de Login
            senha_digitada = json_data.get('senha')
            login_usuario = json_data.get('email') or json_data.get('cpf')

            if not senha_digitada:
                return {"message": "Senha é obrigatória."}, 400
            if not login_usuario:
                 return {"message": "CPF ou Email obrigatório para login."}, 400

            # Verifica duplicidade no Usuário
            if Usuario.query.filter_by(login=login_usuario).first():
                return {"message": "Este Login já está em uso."}, 409

            # 3. Cria o Usuário (CORREÇÃO: Sem Hash Duplo)
            novo_usuario = Usuario(
                nome=dados_validados.get('nome'),
                login=login_usuario,
                senha=senha_digitada, # Envia pura. O Model Usuario criptografa!
                perfil="produtor"
            )

            db.session.add(novo_usuario)
            db.session.flush()

            # 4. Cria o Agricultor
            dados_validados['usuario_id'] = novo_usuario.id
            novo_agricultor = Agricultor(**dados_validados)
            db.session.add(novo_agricultor)
            
            db.session.commit()
            
            return agricultor_schema_detalhado.dump(novo_agricultor), 201

        except Exception as e:
            db.session.rollback()
            return {"message": "Erro interno.", "error": str(e)}, 500

class AgricultorResource(Resource):
    def get(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        return agricultor_schema_detalhado.dump(agricultor)

    def put(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        json_data = request.get_json()
        
        try:
            # partial=True permite editar só o nome sem mandar o CPF
            dados_validados = agricultor_schema_carga.load(json_data, partial=True)
            
            for key, value in dados_validados.items():
                setattr(agricultor, key, value)
                
            db.session.commit()
            return agricultor_schema_detalhado.dump(agricultor)
            
        except ValidationError as err:
            # AQUI ESTÁ O SEU ERRO 400: O Schema rejeitou algum dado (ex: CPF inválido)
            # O front vai receber qual campo está errado.
            return {"messages": err.messages}, 400

    def delete(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        usuario_id_vinculado = agricultor.usuario_id
        
        # Regra de Integridade (RF03)
        if agricultor.solicitacoes or agricultor.propriedades:
            return {"message": "Não é possível excluir: existem registros vinculados."}, 409

        try:
            db.session.delete(agricultor)
            if usuario_id_vinculado:
                usuario = Usuario.query.get(usuario_id_vinculado)
                if usuario:
                    db.session.delete(usuario)

            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao excluir.", "error": str(e)}, 500