from flask import request
from flask_restful import Resource
from models import Veiculo
from helpers.database import db
# CORREÇÃO: Importamos os schemas corretos agora
from schemas import VeiculoListaSchema, VeiculoLoadSchema

# Instâncias dos Schemas
veiculo_schema = VeiculoListaSchema()             # Para mostrar 1 veículo
veiculos_schema_lista = VeiculoListaSchema(many=True) # Para listar vários
veiculo_load_schema = VeiculoLoadSchema()         # Para validar dados recebidos (POST/PUT)

class VeiculoListResource(Resource):
    # LISTAR TODOS (GET /veiculos)
    def get(self):
        veiculos = Veiculo.query.all()
        return veiculos_schema_lista.dump(veiculos)

    # CADASTRAR NOVO (POST /veiculos)
    def post(self):
        json_data = request.get_json()
        try:
            # Carrega e valida os dados usando o LoadSchema
            dados_validados = veiculo_load_schema.load(json_data)
            
            # Cria a instância do Veículo com os dados validados
            novo_veiculo = Veiculo(**dados_validados)
            
            db.session.add(novo_veiculo)
            db.session.commit()
            return veiculo_schema.dump(novo_veiculo), 201
        except Exception as e:
            return {"message": "Erro ao criar veículo", "error": str(e)}, 400

class VeiculoResource(Resource):
    # BUSCAR UM SÓ (GET /veiculos/1)
    def get(self, veiculo_id):
        veiculo = Veiculo.query.get_or_404(veiculo_id)
        return veiculo_schema.dump(veiculo)

    # ATUALIZAR (PUT /veiculos/1)
    def put(self, veiculo_id):
        veiculo = Veiculo.query.get_or_404(veiculo_id)
        json_data = request.get_json()
        
        try:
            # Valida os dados (partial=True permite enviar só o campo que mudou)
            dados_validados = veiculo_load_schema.load(json_data, partial=True)
            
            # Atualiza os campos automaticamente
            for key, value in dados_validados.items():
                setattr(veiculo, key, value)

            db.session.commit()
            return veiculo_schema.dump(veiculo)
            
        except Exception as e:
            return {"message": "Erro ao atualizar veículo", "error": str(e)}, 400

    # DELETAR (DELETE /veiculos/1)
    def delete(self, veiculo_id):
        veiculo = Veiculo.query.get_or_404(veiculo_id)
        
        # Verifica se o veículo está sendo usado antes de deletar (Opcional, mas recomendado)
        if veiculo.solicitacoes:
             # Se tiver histórico, talvez seja melhor apenas desativar, mas aqui vamos deletar
             pass 

        db.session.delete(veiculo)
        db.session.commit()
        return '', 204