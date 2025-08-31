from flask import request
from flask_restful import Resource
from models import Propriedade, Agricultor
from helpers.database import db, ma
from marshmallow import fields, ValidationError
from flask_jwt_extended import jwt_required

# --- Schemas ---
class PropriedadeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Propriedade
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    agricultor_id = fields.Int(required=True)
    solicitacoes = fields.Nested("resources.solicitacao.SolicitacaoSchema", many=True, dump_only=True)

propriedade_schema = PropriedadeSchema()
propriedades_schema = PropriedadeSchema(many=True)

# --- Resources ---
class AllPropriedadesListResource(Resource):
    @jwt_required()
    def get(self):
        propriedades = Propriedade.query.all()
        return propriedades_schema.dump(propriedades)

class PropriedadeListResource(Resource):
    @jwt_required()
    def get(self, agricultor_id):
        Agricultor.query.get_or_404(agricultor_id)
        propriedades = Propriedade.query.filter_by(agricultor_id=agricultor_id).all()
        return propriedades_schema.dump(propriedades)

    @jwt_required()
    def post(self, agricultor_id):
        Agricultor.query.get_or_404(agricultor_id)
        json_data = request.get_json()
        json_data['agricultor_id'] = agricultor_id

        try:
            propriedade = propriedade_schema.load(json_data)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.add(propriedade)
        db.session.commit()
        
        return propriedade_schema.dump(propriedade), 201

class PropriedadeResource(Resource):
    @jwt_required()
    def get(self, propriedade_id):
        propriedade = Propriedade.query.get_or_404(propriedade_id)
        return propriedade_schema.dump(propriedade)

    @jwt_required()
    def put(self, propriedade_id):
        propriedade = Propriedade.query.get_or_404(propriedade_id)
        json_data = request.get_json()

        try:
            propriedade = propriedade_schema.load(json_data, instance=propriedade, partial=True)
        except ValidationError as err:
            return {"messages": err.messages}, 400
        
        db.session.commit()
        return propriedade_schema.dump(propriedade)

    @jwt_required()
    def delete(self, propriedade_id):
        propriedade = Propriedade.query.get_or_404(propriedade_id)
        db.session.delete(propriedade)
        db.session.commit()
        return '', 204