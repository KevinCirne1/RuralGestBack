from __future__ import annotations
from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Servico(db.Model):
    __tablename__ = 'servico'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_servico: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(String(200), nullable=True)
    
    # --- NOVO CAMPO ---
    # Define qual tipo de veículo é necessário (Ex: "Trator", "Caminhão")
    # Se for nulo, significa que o serviço não precisa de veículo (ex: "Consultoria Técnica")
    tipo_veiculo: Mapped[str] = mapped_column(String(50), nullable=True)
    
    capacidade_hectares: Mapped[float] = mapped_column(nullable=True)

    def to_json(self):
        return {
            "id": self.id,
            "nome_servico": self.nome_servico,
            "descricao": self.descricao,
            "tipo_veiculo": self.tipo_veiculo, # Retorna no JSON
            "capacidade_hectares": self.capacidade_hectares
        }