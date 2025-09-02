# ==============================================================================
# FICHEIRO 8: models/agricultor.py (Refatorado com backref)
# ==============================================================================
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime
from helpers.database import db

class Agricultor(db.Model):
    __tablename__ = 'agricultor'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    cpf: Mapped[str] = mapped_column(String(20), unique=True)
    comunidade: Mapped[str] = mapped_column(String(100))
    contato: Mapped[str] = mapped_column(String(20))
    data_atualizacao_cadastro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # A definição explícita dos relacionamentos foi movida para o outro lado da relação ("many-to-one")
    # O backref irá criar as propriedades 'propriedades' e 'solicitacoes' aqui automaticamente.
