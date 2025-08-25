from helpers.database import db
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime

class Agricultor(db.Model):
    __tablename__ = 'agricultor'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    comunidade: Mapped[str] = mapped_column(String(100), nullable=False)
    contato: Mapped[str] = mapped_column(String(20), nullable=True)
    data_atualizacao_cadastro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
