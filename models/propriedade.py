from __future__ import annotations
from typing import List
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from helpers.database import db

class Propriedade(db.Model):
    __tablename__ = 'propriedade'

    id: Mapped[int] = mapped_column(primary_key=True)
    terreno: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo_agricultura: Mapped[str] = mapped_column(String(100))
    area_total: Mapped[float] = mapped_column(Float)
    area_exploravel: Mapped[float] = mapped_column(Float)
    coordenadas_geograficas: Mapped[str] = mapped_column(String(50))
    
    agricultor_id: Mapped[int] = mapped_column(ForeignKey('agricultor.id'), nullable=False)
    
    # Relacionamentos
    agricultor: Mapped["Agricultor"] = relationship(back_populates="propriedades")
    solicitacoes: Mapped[List["Solicitacao"]] = relationship(back_populates="propriedade", cascade="all, delete-orphan")