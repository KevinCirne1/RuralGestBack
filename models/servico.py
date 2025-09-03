
from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float
from helpers.database import db

class Servico(db.Model):
    __tablename__ = 'servico'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_servico: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str] = mapped_column(String(255))
    capacidade_hectares: Mapped[float] = mapped_column(Float, nullable=True)

    # A propriedade 'solicitacoes' será criada automaticamente pelo backref em Solicitacao.
