from flask import request
from flask_restful import Resource
from models.usuario import Usuario
from models.agricultor import Agricultor
from helpers.database import db
from schemas import UsuarioDetalhadoSchema, AgricultorLoadSchema

# Instância do schema para este resource
usuario_schema_detalhado = UsuarioDetalhadoSchema()
agricultor_schema_detalhado = AgricultorLoadSchema()

class LoginResource(Resource):
    def post(self):
        json_data = request.get_json()
        
        # Pega os dados brutos
        login = json_data.get('login')
        senha = json_data.get('senha')

        if not login or not senha:
            return {"message": "Login e senha são obrigatórios"}, 400

        # Busca no banco
        utilizador = Usuario.query.filter_by(login=login).first()

        # Verifica se o usuário existe E se a senha bate
        # IMPORTANTE: Usamos o método do próprio model, que usa o Bcrypt correto
        if utilizador and utilizador.verificar_senha(senha):
            
            # Gera o JSON do usuário
            response = usuario_schema_detalhado.dump(utilizador)
            
            # Busca dados extras se for produtor/agricultor
            if utilizador.perfil in ['agricultor', 'produtor']:
                agricultor = Agricultor.query.filter_by(usuario_id=utilizador.id).first()
                if agricultor:
                    response['agricultor_id'] = agricultor.id
            
            return response, 200
        
        return {"message": "Credenciais inválidas"}, 401

class RegistroAgricultorResource(Resource):
    def post(self):
        json_data = request.get_json()
        
        # Validação de campos obrigatórios
        required_fields = ['nome', 'login', 'senha', 'cpf', 'comunidade']
        for field in required_fields:
            if field not in json_data:
                if field == 'login' and 'cpf' in json_data:
                    json_data['login'] = json_data['cpf']
                else:
                    return {"message": f"O campo '{field}' é obrigatório."}, 400

        try:
            # Tratamento básico
            login_str = str(json_data.get('login')).strip()
            cpf_str = str(json_data.get('cpf')).strip()
            senha_str = str(json_data.get('senha')).strip()

            # Verificação de duplicidade
            if Usuario.query.filter_by(login=login_str).first():
                return {"message": "Este login já está em uso."}, 409
            
            if Agricultor.query.filter_by(cpf=cpf_str).first():
                return {"message": "Este CPF já está registrado."}, 409

            # --- CORREÇÃO CRÍTICA AQUI ---
            # NÃO criptografamos a senha aqui. Passamos ela 'crua' (senha_str).
            # O __init__ do Model Usuario vai fazer o hash automaticamente.
            novo_usuario = Usuario(
                nome=json_data.get('nome'),
                login=login_str,
                senha=senha_str, # Passa a senha normal
                perfil='agricultor' # Padronizado como 'agricultor' para bater com o front
            )
            
            db.session.add(novo_usuario)
            db.session.flush() # Gera o ID

            # Criação do Agricultor vinculado
            novo_agricultor = Agricultor(
                nome=json_data.get('nome'), 
                cpf=cpf_str,
                comunidade=json_data.get('comunidade'),
                contato=json_data.get('contato'),
                usuario_id=novo_usuario.id 
            )
            
            db.session.add(novo_agricultor)
            db.session.commit()
            
            # Prepara resposta com ID correto
            user_response = usuario_schema_detalhado.dump(novo_usuario)
            user_response['agricultor_id'] = novo_agricultor.id

            return {
                "message": "Conta criada com sucesso!",
                "usuario": user_response
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"message": "Erro interno ao registrar.", "error": str(e)}, 500