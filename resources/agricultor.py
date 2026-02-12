from flask import request
from flask_restful import Resource
from models import Agricultor, Usuario  
from helpers.database import db
from marshmallow import ValidationError


from schemas import (
    AgricultorDetalhadoSchema, 
    AgricultorListaSchema, 
    AgricultorLoadSchema
)

#Instâncias dos Schemas
agricultor_schema_detalhado = AgricultorDetalhadoSchema()
agricultores_schema_lista = AgricultorListaSchema(many=True)
agricultor_schema_carga = AgricultorLoadSchema()



class AgricultorListResource(Resource):
    def get(self):
        agricultores = Agricultor.query.all()
        return agricultores_schema_lista.dump(agricultores)

    def post(self):
        json_data = request.get_json()
        
        # 1. Valida os dados do Agricultor (Marshmallow)
        try:
            dados_validados = agricultor_schema_carga.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400

        # --- Início da Lógica de Usuário + Agricultor ---
        try:
            # 2. Captura a Senha (Obrigatória na criação)
            senha_digitada = json_data.get('senha')
            if not senha_digitada:
                return {"message": "A senha é obrigatória para criar o acesso do agricultor."}, 400

            # 3. Define o Login (Prioridade: Email -> CPF)
            login_usuario = json_data.get('email')
            if not login_usuario:
                login_usuario = json_data.get('cpf')

            if not login_usuario:
                 return {"message": "É necessário fornecer CPF ou Email para o login."}, 400

            # Verifica se já existe esse login em Usuário para evitar erro 500 feio
            if Usuario.query.filter_by(login=login_usuario).first():
                return {"message": "Este Login (CPF ou Email) já está em uso."}, 409

            # 4. Cria o Usuário
            novo_usuario = Usuario(
                nome=dados_validados.get('nome'),
                login=login_usuario,
                senha = senha_digitada, # Criptografa a senha
                perfil="produtor" # Define o perfil fixo
            )

            # Adiciona e faz flush para gerar o ID do usuário imediatamente
            db.session.add(novo_usuario)
            db.session.flush()

            # 5. Cria o Agricultor vinculado ao ID do Usuário criado
            dados_validados['usuario_id'] = novo_usuario.id
            
            novo_agricultor = Agricultor(**dados_validados)
            db.session.add(novo_agricultor)
            
            # 6. Salva tudo no banco (Commit único)
            db.session.commit()
            
            return agricultor_schema_detalhado.dump(novo_agricultor), 201

        except Exception as e:
            # Se der erro (ex: Login duplicado ou erro de banco), desfaz tudo
            db.session.rollback()
            return {"message": "Erro ao criar agricultor e usuário.", "error": str(e)}, 500

class AgricultorResource(Resource):
    def get(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        return agricultor_schema_detalhado.dump(agricultor)

    def put(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        json_data = request.get_json()
        try:
            dados_validados = agricultor_schema_carga.load(json_data, partial=True)
            for key, value in dados_validados.items():
                setattr(agricultor, key, value)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.commit()
        return agricultor_schema_detalhado.dump(agricultor)

    def delete(self, agricultor_id):
        # 1. Busca o agricultor
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        
        # 2. Captura o ID do usuário vinculado ANTES de deletar o agricultor
        usuario_id_vinculado = agricultor.usuario_id
        
        try:
            # 3. Deleta o registro da tabela Agricultor
            db.session.delete(agricultor)
            
            # 4. Se havia um usuário vinculado, deleta ele também da tabela Usuario
            if usuario_id_vinculado:
                usuario = Usuario.query.get(usuario_id_vinculado)
                if usuario:
                    db.session.delete(usuario)

            # 5. Confirma as duas exclusões no banco
            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao excluir o registro.", "error": str(e)}, 500