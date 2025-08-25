from flask import request
from flask_restful import Resource
from models.agricultor import Agricultor
from helpers.database import db, ma
from marshmallow import fields, ValidationError
from sqlalchemy.exc import IntegrityError


class AgricultorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Agricultor
        load_instance = True
    
    id = fields.Int(dump_only=True)
    data_atualizacao_cadastro = fields.DateTime(dump_only=True)
    nome = fields.Str(required=True)
    cpf = fields.Str(required=True)
    comunidade = fields.Str(required=True)
    
    # Adiciona o campo para mostrar as propriedades aninhadas na resposta
    # Usar o caminho completo para o schema evita problemas de importação circular.
    propriedades = fields.Nested("resources.propriedade.PropriedadeSchema", many=True, dump_only=True)

agricultor_schema = AgricultorSchema()
agricultores_schema = AgricultorSchema(many=True)


class AgricultorListResource(Resource):
    def get(self):
        agricultores = Agricultor.query.all()
        return agricultores_schema.dump(agricultores)

    def post(self):
        json_data = request.get_json()
        try:
            agricultor = agricultor_schema.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400

        try:
            db.session.add(agricultor)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Erro ao criar agricultor. CPF já pode existir no sistema."}, 400
        
        return agricultor_schema.dump(agricultor), 201

class AgricultorResource(Resource):
    def get(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        return agricultor_schema.dump(agricultor)

    def put(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        json_data = request.get_json()
        
        try:
            agricultor = agricultor_schema.load(json_data, instance=agricultor, partial=True)
        except ValidationError as err:
            return {"messages": err.messages}, 400

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Erro ao atualizar agricultor. CPF já pode existir no sistema."}, 400
        
        return agricultor_schema.dump(agricultor)

    def delete(self, agricultor_id):
        agricultor = Agricultor.query.get_or_404(agricultor_id)
        db.session.delete(agricultor)
        db.session.commit()
        return '', 204