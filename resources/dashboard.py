from flask_restful import Resource
from sqlalchemy import func
from helpers.database import db
from models import Agricultor, Solicitacao, Servico, Propriedade

class DashboardResumoResource(Resource):
    def get(self):
        """Devolve os contadores principais para os cartões do topo do dashboard"""
        total_agricultores = db.session.query(func.count(Agricultor.id)).scalar()
        total_solicitacoes = db.session.query(func.count(Solicitacao.id)).scalar()
        total_hectares = db.session.query(func.sum(Propriedade.area_total)).scalar() or 0
        
        # Contagem por status
        pendentes = Solicitacao.query.filter_by(status='Pendente').count()
        em_andamento = Solicitacao.query.filter_by(status='Em Andamento').count()
        concluidas = Solicitacao.query.filter_by(status='Concluído').count()

        return {
            "total_agricultores": total_agricultores,
            "total_solicitacoes": total_solicitacoes,
            "total_hectares_cadastrados": round(total_hectares, 2),
            "solicitacoes_status": {
                "pendentes": pendentes,
                "em_andamento": em_andamento,
                "concluidas": concluidas
            }
        }, 200

class DashboardGraficosResource(Resource):
    def get(self):
        """Devolve dados formatados para gráficos (ex: Pizza ou Barras)"""
        
        # 1. Serviços mais solicitados
        # SQL equivalente: SELECT nome_servico, COUNT(*) FROM solicitacao JOIN servico ... GROUP BY nome_servico
        servicos_populares = db.session.query(
            Servico.nome_servico, func.count(Solicitacao.id)
        ).join(Solicitacao).group_by(Servico.nome_servico).all()

        dados_grafico_servicos = [
            {"name": nome, "value": contagem} for nome, contagem in servicos_populares
        ]

        return {
            "servicos_populares": dados_grafico_servicos,
            # Pode adicionar mais gráficos aqui (ex: Solicitações por Mês)
        }, 200