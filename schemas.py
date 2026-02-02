from helpers.database import ma
from marshmallow import fields, EXCLUDE

# --- Schemas de Visualização 

# Schemas Simples 
class AgricultorSimplesSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str()

class PropriedadeSimplesSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    terreno = fields.Str()

class UsuarioSimplesSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str()

class ServicoSimplesSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome_servico = fields.Str()
    tipo_veiculo = fields.Str()

# Schema Simples do Veículo
class VeiculoSimplesSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str()
    status = fields.Str()

class SolicitacaoSimplesSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    data_solicitacao = fields.DateTime()
    status = fields.Str()

# --- Schemas de Lista ---

class AgricultorListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str()
    cpf = fields.Str()
    comunidade = fields.Str()
    contato = fields.Str()
    data_atualizacao_cadastro = fields.DateTime()

class PropriedadeListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    terreno = fields.Str()
    tipo_agricultura = fields.Str()
    area_total = fields.Float()
    area_exploravel = fields.Float()
    coordenadas_geograficas = fields.Str()
    agricultor_id = fields.Int()
    
    # --- NOVO: Adicionado para visualizar no Dashboard e Tabelas ---
    cultura_principal = fields.Str()
    quantidade_gado = fields.Int()

class UsuarioListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str()
    login = fields.Email()
    perfil = fields.Str()

class ServicoListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome_servico = fields.Str()
    descricao = fields.Str()
    tipo_veiculo = fields.Str()

# Schema de Lista de Veículos
class VeiculoListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str()
    placa = fields.Str()
    tipo = fields.Str()
    status = fields.Str()

class SolicitacaoListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    data_solicitacao = fields.DateTime()
    status = fields.Str()
    agricultor = fields.Nested(AgricultorSimplesSchema, dump_only=True)
    servico = fields.Nested(ServicoSimplesSchema, dump_only=True)
    propriedade = fields.Nested(PropriedadeSimplesSchema, dump_only=True)
    veiculo = fields.Nested(VeiculoSimplesSchema, dump_only=True)
    motivo_recusa = fields.Str()

# --- Schemas de Detalhe ---

class PropriedadeDetalhadoSchema(PropriedadeListaSchema):
    agricultor = fields.Nested(AgricultorSimplesSchema, dump_only=True)

class AgricultorDetalhadoSchema(AgricultorListaSchema):
    propriedades = fields.Nested("PropriedadeSimplesSchema", many=True, dump_only=True)
    solicitacoes = fields.Nested("SolicitacaoSimplesSchema", many=True, dump_only=True)

class UsuarioDetalhadoSchema(UsuarioListaSchema):
    solicitacoes_atendidas = fields.Nested("SolicitacaoSimplesSchema", many=True, dump_only=True)

class SolicitacaoDetalhadoSchema(SolicitacaoListaSchema):
    data_execucao = fields.DateTime()
    propriedade = fields.Nested(PropriedadeSimplesSchema, dump_only=True)
    operador = fields.Nested(UsuarioSimplesSchema, dump_only=True)
    veiculo = fields.Nested(VeiculoSimplesSchema, dump_only=True)


# --- Schemas de Carga (Load) ---

class BaseLoadSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

class AgricultorLoadSchema(BaseLoadSchema):
    nome = fields.Str(required=True)
    cpf = fields.Str(required=True)
    comunidade = fields.Str(required=True)
    contato = fields.Str(required=True)

class PropriedadeLoadSchema(BaseLoadSchema):
    terreno = fields.Str(required=True)
    tipo_agricultura = fields.Str(required=True)
    area_total = fields.Float(required=True)
    area_exploravel = fields.Float(required=True)
    coordenadas_geograficas = fields.Str(required=True)
    agricultor_id = fields.Int()
    
    # --- NOVO: Adicionado para permitir SALVAR (POST/PUT) ---
    cultura_principal = fields.Str(allow_none=True)
    quantidade_gado = fields.Int(load_default=0)

class UsuarioLoadSchema(BaseLoadSchema):
    nome = fields.Str(required=True)
    login = fields.Email(required=True)
    senha = fields.Str(required=True, load_only=True)
    perfil = fields.Str(required=True)

class ServicoLoadSchema(BaseLoadSchema):
    nome_servico = fields.Str(required=True)
    descricao = fields.Str()
    capacidade_hectares = fields.Float()
    tipo_veiculo = fields.Str(allow_none=True)

class VeiculoLoadSchema(BaseLoadSchema):
    nome = fields.Str(required=True)
    placa = fields.Str(allow_none=True)
    tipo = fields.Str(required=True)
    status = fields.Str() 

class SolicitacaoLoadSchema(BaseLoadSchema):
    agricultor_id = fields.Int(required=True)
    propriedade_id = fields.Int(required=True)
    servico_id = fields.Int(required=True)
    operador_id = fields.Int(allow_none=True)
    veiculo_id = fields.Int(allow_none=True)
    status = fields.Str()
    data_execucao = fields.DateTime(allow_none=True)
    motivo_recusa = fields.Str(allow_none=True)