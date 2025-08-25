from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, Float

class Servico(db.Model):
    __tablename__ = 'servico'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_servico: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=True)
    capacidade_hectares: Mapped[float] = mapped_column(Float, nullable=True)

