from flask import request
from flask_restful import Resource
from models.servico import Servico
from helpers.database import db, ma
from marshmallow import fields, ValidationError
from sqlalchemy.exc import IntegrityError

# --- Schemas ---
class ServicoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Servico
        load_instance = True
    
    id = fields.Int(dump_only=True)
    nome_servico = fields.Str(required=True)

servico_schema = ServicoSchema()
servicos_schema = ServicoSchema(many=True)

# --- Resources ---
class ServicoListResource(Resource):
    def get(self):
        return servicos_schema.dump(Servico.query.all())
    def post(self):
        json_data = request.get_json()
        try:
            servico = servico_schema.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        try:
            db.session.add(servico)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Serviço com este nome já existe."}, 400
        return servico_schema.dump(servico), 201

class ServicoResource(Resource):
    def get(self, servico_id):
        return servico_schema.dump(Servico.query.get_or_404(servico_id))
    def delete(self, servico_id):
        servico = Servico.query.get_or_404(servico_id)
        db.session.delete(servico)
        db.session.commit()
        return '', 204
