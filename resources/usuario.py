from flask import request
from flask_restful import Resource
from models import Usuario
from helpers.database import db
from marshmallow import ValidationError
from schemas import (
    UsuarioDetalhadoSchema, 
    UsuarioListaSchema, 
    UsuarioLoadSchema
)

# --- Instâncias dos Schemas ---
usuario_schema_detalhado = UsuarioDetalhadoSchema()
usuarios_schema_lista = UsuarioListaSchema(many=True)
usuario_schema_carga = UsuarioLoadSchema()

# --- Resources ---

class UsuarioListResource(Resource):
    def get(self):
        usuarios = Usuario.query.all()
        return usuarios_schema_lista.dump(usuarios)

    def post(self):
        json_data = request.get_json()
        try:
            # Carrega e valida os dados (incluindo contato)
            dados_validados = usuario_schema_carga.load(json_data)
            
            # Cria o usuário passando todos os dados validados
            # Como atualizamos o __init__ do Model, ele vai aceitar o contato aqui
            novo_usuario = Usuario(**dados_validados)
            
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.add(novo_usuario)
        db.session.commit()
        return usuario_schema_detalhado.dump(novo_usuario), 201

class UsuarioResource(Resource):
    def get(self, usuario_id):
        usuario = Usuario.query.get_or_404(usuario_id)
        return usuario_schema_detalhado.dump(usuario)

    # --- MÉTODO DE EDIÇÃO (FALTAVA ISSO) ---
    def put(self, usuario_id):
        usuario = Usuario.query.get_or_404(usuario_id)
        json_data = request.get_json()
        
        try:
            # partial=True permite enviar apenas alguns campos para atualizar
            dados = usuario_schema_carga.load(json_data, partial=True)
        except ValidationError as err:
            return {"messages": err.messages}, 400

        # Atualiza os campos se eles vierem na requisição
        if 'nome' in dados: usuario.nome = dados['nome']
        if 'login' in dados: usuario.login = dados['login']
        if 'perfil' in dados: usuario.perfil = dados['perfil']
        if 'contato' in dados: usuario.contato = dados['contato'] # <--- Atualiza contato
        
        # Só atualiza a senha se ela for enviada
        if 'senha' in dados and dados['senha']:
            usuario.senha = dados['senha']

        db.session.commit()
        return usuario_schema_detalhado.dump(usuario)

    def delete(self, usuario_id):
        usuario = Usuario.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204