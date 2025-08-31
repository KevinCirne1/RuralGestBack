from helpers.database import ma
from marshmallow import fields

# --- Schemas de Lista (sem relacionamentos profundos) ---

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

class UsuarioListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str()
    login = fields.Email()
    perfil = fields.Str()

class ServicoListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nome_servico = fields.Str()

class SolicitacaoListaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    data_solicitacao = fields.DateTime()
    status = fields.Str()
    agricultor = fields.Nested(AgricultorListaSchema, dump_only=True)
    servico = fields.Nested(ServicoListaSchema, dump_only=True)

# --- Schemas Detalhados (com relacionamentos) ---

class PropriedadeDetalhadoSchema(PropriedadeListaSchema):
    area_exploravel = fields.Float()
    coordenadas_geograficas = fields.Str()

class AgricultorDetalhadoSchema(AgricultorListaSchema):
    propriedades = fields.Nested(PropriedadeDetalhadoSchema, many=True, dump_only=True)
    solicitacoes = fields.Nested(SolicitacaoListaSchema, many=True, dump_only=True)

class SolicitacaoDetalhadoSchema(SolicitacaoListaSchema):
    data_execucao = fields.DateTime()
    propriedade = fields.Nested(PropriedadeDetalhadoSchema, dump_only=True)
    operador = fields.Nested(UsuarioListaSchema, dump_only=True)

# --- Schemas de Carga (para validar dados de entrada em POST/PUT) ---
# AGORA SÃO EXPLÍCITOS PARA EVITAR ERROS

class AgricultorLoadSchema(ma.Schema):
    nome = fields.Str(required=True)
    cpf = fields.Str(required=True)
    comunidade = fields.Str(required=True)
    contato = fields.Str()

class PropriedadeLoadSchema(ma.Schema):
    terreno = fields.Str(required=True)
    tipo_agricultura = fields.Str()
    area_total = fields.Float()
    area_exploravel = fields.Float()
    coordenadas_geograficas = fields.Str()

class UsuarioLoadSchema(ma.Schema):
    nome = fields.Str(required=True)
    login = fields.Email(required=True)
    senha = fields.Str(required=True, load_only=True)
    perfil = fields.Str(required=True)

class ServicoLoadSchema(ma.Schema):
    nome_servico = fields.Str(required=True)
    descricao = fields.Str()
    capacidade_hectares = fields.Float()

class SolicitacaoLoadSchema(ma.Schema):
    agricultor_id = fields.Int(required=True)
    propriedade_id = fields.Int(required=True)
    servico_id = fields.Int(required=True)
    operador_id = fields.Int()
    status = fields.Str()
    data_execucao = fields.DateTime()
