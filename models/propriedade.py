from __future__ import annotations
from typing import Optional # Importante para campos opcionais
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, Integer
from helpers.database import db

class Propriedade(db.Model):
    __tablename__ = 'propriedade'

    id: Mapped[int] = mapped_column(primary_key=True)
    terreno: Mapped[str] = mapped_column(String(150))
    tipo_agricultura: Mapped[str] = mapped_column(String(100))
    area_total: Mapped[float] = mapped_column(Float)
    area_exploravel: Mapped[float] = mapped_column(Float)
    coordenadas_geograficas: Mapped[str] = mapped_column(String(50))
    
    # --- NOVAS COLUNAS (Adicionadas para o Dashboard) ---
    # Mapped[str | None] diz que o campo pode ser Texto ou Vazio (Null) no banco
    cultura_principal: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # default=0 garante que se não vier nada, salva como 0
    quantidade_gado: Mapped[int] = mapped_column(Integer, default=0) 
    # ----------------------------------------------------

    agricultor_id: Mapped[int] = mapped_column(ForeignKey("agricultor.id"))

    agricultor: Mapped["Agricultor"] = relationship(backref="propriedades")