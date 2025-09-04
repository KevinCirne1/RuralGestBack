
from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey
from helpers.database import db

class Propriedade(db.Model):
    __tablename__ = 'propriedade'

    id: Mapped[int] = mapped_column(primary_key=True)
    terreno: Mapped[str] = mapped_column(String(150))
    tipo_agricultura: Mapped[str] = mapped_column(String(100))
    area_total: Mapped[float] = mapped_column(Float)
    area_exploravel: Mapped[float] = mapped_column(Float)
    coordenadas_geograficas: Mapped[str] = mapped_column(String(50))
    
    agricultor_id: Mapped[int] = mapped_column(ForeignKey("agricultor.id"))

    
    agricultor: Mapped["Agricultor"] = relationship(backref="propriedades")
    
