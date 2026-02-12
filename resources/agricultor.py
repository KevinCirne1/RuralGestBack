from flask import request
from flask_restful import Resource
from models import Agricultor, Usuario  
from helpers.database import db
from marshmallow import ValidationError

# NOTA: Não importamos werkzeug aqui para evitar o Hash Duplo.
# O seu model Usuario já faz a criptografia no __init__.

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
        print("\n>>> DEBUG: POST /agricultores")
        json_data = request.get_json()
        
        # 1. Valida os dados do Agricultor (Nome, Comunidade, etc)
        try:
            dados_validados = agricultor_schema_carga.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400

        # --- Início da Lógica de Usuário + Agricultor ---
        try:
            # 2. Captura dados de Login
            senha_digitada = json_data.get('senha')
            # Tenta pegar email, se não tiver, pega cpf para usar de login
            login_usuario = json_data.get('email') or json_data.get('cpf')

            if not senha_digitada:
                return {"message": "A senha é obrigatória para criar o acesso."}, 400
            
            if not login_usuario:
                 return {"message": "É necessário fornecer CPF ou Email para o login."}, 400

            # Verifica se já existe esse login em Usuário
            if Usuario.query.filter_by(login=login_usuario).first():
                return {"message": "Este Login (CPF ou Email) já está em uso."}, 409

            # 3. Cria o Usuário
            # ATENÇÃO: Passamos 'senha_digitada' PURA. O Model Usuario criptografa sozinho!
            novo_usuario = Usuario(
                nome=dados_validados.get('nome'),
                login=login_usuario,
                senha=senha_digitada, 
                perfil="agricultor" # Define o perfil fixo para o front saber onde redirecionar
            )

            # Adiciona e faz flush para gerar o ID do usuário imediatamente
            db.session.add(novo_usuario)
            db.session.flush() 

            # 4. Cria o Agricultor vinculado ao ID do Usuário criado
            dados_validados['usuario_id'] = novo_usuario.id
            
            novo_agricultor = Agricultor(**dados_validados)
            db.session.add(novo_agricultor)
            
            # 5. Salva tudo no banco (Commit único)
            db.session.commit()
            
            print(f">>> Sucesso: Agricultor {novo_agricultor.nome} criado com ID {novo_agricultor.id}")
            return agricultor_schema_detalhado.dump(novo_agricultor), 201

        except Exception as e:
            # Se der erro (ex: Login duplicado ou erro de banco), desfaz tudo
            db.session.rollback()
            print(f">>> Erro Crítico: {str(e)}")
            return {"message": "Erro ao criar agricultor e usuário.", "error": str(e)}, 500

class AgricultorResource(Resource):
    def get(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        return agricultor_schema_detalhado.dump(agricultor)

    def put(self, agricultor_id):
        print(f"\n>>> DEBUG: PUT /agricultores/{agricultor_id}")
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        json_data = request.get_json()
        
        try:
            # CORREÇÃO DO ERRO 400: partial=True
            # Isso permite editar só o telefone sem precisar mandar o CPF de novo
            dados_validados = agricultor_schema_carga.load(json_data, partial=True)
            
            # Se o front mandar 'comprovante_residencia', mapeamos para o banco se necessário
            # (Adicione logica de mapeamento aqui se os nomes forem diferentes no model)

            for key, value in dados_validados.items():
                setattr(agricultor, key, value)
                
            db.session.commit()
            return agricultor_schema_detalhado.dump(agricultor)
            
        except ValidationError as err:
            # Esse print vai aparecer no seu terminal se der erro 400 de novo
            print(f">>> Erro de Validação no PUT: {err.messages}")
            return {"messages": err.messages}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro interno.", "error": str(e)}, 500

    def delete(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        usuario_id_vinculado = agricultor.usuario_id
        
        # Regra de integridade: Não apaga se tiver histórico
        if agricultor.solicitacoes or agricultor.propriedades:
            return {"message": "Não é possível excluir: existem registros vinculados."}, 409

        try:
            db.session.delete(agricultor)
            
            # Se havia um usuário vinculado, deleta ele também
            if usuario_id_vinculado:
                usuario = Usuario.query.get(usuario_id_vinculado)
                if usuario:
                    db.session.delete(usuario)

            db.session.commit()
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao excluir o registro.", "error": str(e)}, 500