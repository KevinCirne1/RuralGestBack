from __future__ import annotations
from typing import List
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from helpers.database import db

class Servico(db.Model):
    __tablename__ = 'servico'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_servico: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(255))
    capacidade_hectares: Mapped[float] = mapped_column(Float, nullable=True)

    # Relacionamentos
    solicitacoes: Mapped[List["Solicitacao"]] = relationship(back_populates="servico")
