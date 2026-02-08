from flask import request
from flask_restful import Resource
from models.usuario import Usuario
from models.agricultor import Agricultor
from helpers.database import db
from schemas import UsuarioDetalhadoSchema, AgricultorLoadSchema, UsuarioLoadSchema
from marshmallow import ValidationError

# Instância do schema para este resource
usuario_schema_detalhado = UsuarioDetalhadoSchema()
agricultor_schema_detalhado = AgricultorLoadSchema()

class LoginResource(Resource):
    def post(self):
        json_data = request.get_json()
        login = json_data.get('login')
        senha = json_data.get('senha')

        if not login or not senha:
            return {"message": "Login e senha são obrigatórios"}, 400

        utilizador = Usuario.query.filter_by(login=login).first()

        if utilizador and utilizador.verificar_senha(senha):
            # 1. Gera o JSON padrão do usuário
            response = usuario_schema_detalhado.dump(utilizador)
            
            # 2. SE for agricultor, busca o ID dele e INJETA na resposta
            if utilizador.perfil == 'agricultor':
                # Busca o agricultor que tem este usuario_id
                agricultor = Agricultor.query.filter_by(usuario_id=utilizador.id).first()
                if agricultor:
                    # Adiciona o campo mágico que o Frontend está esperando
                    response['agricultor_id'] = agricultor.id
                    # Se quiser mandar o objeto completo, descomente abaixo:
                    # response['agricultor'] = agricultor_schema_detalhado.dump(agricultor)
            
            return response, 200
        
        return {"message": "Credenciais inválidas"}, 401
    
class RegistroAgricultorResource(Resource):
    def post(self):
        """
        Cria um Usuário (login) e um Agricultor (perfil) numa única transação.
        Usado tanto pelo Admin no Dashboard quanto pelo Agricultor na tela de Sign Up.
        """
        json_data = request.get_json()
        
        # Validação básica de campos obrigatórios
        required_fields = ['nome', 'login', 'senha', 'cpf', 'comunidade']
        for field in required_fields:
            if field not in json_data:
                return {"message": f"O campo '{field}' é obrigatório."}, 400

        try:
            # 1. Verifica se o login já existe
            if Usuario.query.filter_by(login=json_data.get('login')).first():
                return {"message": "Este login/email já está em uso."}, 409
            
            # 2. Verifica se o CPF já existe
            if Agricultor.query.filter_by(cpf=json_data.get('cpf')).first():
                return {"message": "Este CPF já está registado."}, 409

            # 3. Cria o Usuário (Login)
            # Forçamos o perfil 'agricultor' aqui
            novo_usuario = Usuario(
                nome=json_data.get('nome'),
                login=json_data.get('login'),
                senha=json_data.get('senha'),
                perfil='agricultor' 
            )
            
            db.session.add(novo_usuario)
            db.session.flush() # Gera o ID do usuário sem fechar a transação

            # 4. Cria o Perfil de Agricultor e VINCULA ao Usuário criado
            novo_agricultor = Agricultor(
                nome=json_data.get('nome'), 
                cpf=json_data.get('cpf'),
                comunidade=json_data.get('comunidade'),
                contato=json_data.get('contato'),
                usuario_id=novo_usuario.id # <-- AQUI ESTÁ O VÍNCULO MÁGICO
            )
            
            db.session.add(novo_agricultor)

            # 5. Salva tudo de uma vez (Transação Atómica)
            db.session.commit()
            
            return {
                "message": "Conta criada com sucesso!",
                "usuario": usuario_schema_detalhado.dump(novo_usuario),
                "agricultor": agricultor_schema_detalhado.dump(novo_agricultor)
            }, 201

        except Exception as e:
            db.session.rollback() # Se der erro em qualquer parte, desfaz tudo
            return {"message": "Erro interno ao registar.", "error": str(e)}, 500
