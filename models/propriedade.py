from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, ForeignKey

class Propriedade(db.Model):
    __tablename__ = 'propriedade'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    terreno: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_agricultura: Mapped[str] = mapped_column(String(100))
    area_total: Mapped[float] = mapped_column(Float)
    area_exploravel: Mapped[float] = mapped_column(Float)
    coordenadas_geograficas: Mapped[str] = mapped_column(String(50))

    agricultor_id: Mapped[int] = mapped_column(ForeignKey("agricultor.id"), nullable=False)
    # --- RELACIONAMENTO ---
    # 'backref' cria a propriedade 'propriedades' no modelo Agricultor automaticamente.
    agricultor: Mapped["Agricultor"] = relationship(backref="propriedades")

