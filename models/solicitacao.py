# ==============================================================================
# FICHEIRO 12: models/solicitacao.py (Refatorado com backref)
# ==============================================================================
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String, ForeignKey
from helpers.database import db

class Solicitacao(db.Model):
    __tablename__ = 'solicitacao'

    id: Mapped[int] = mapped_column(primary_key=True)
    data_solicitacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data_execucao: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Pendente')

    agricultor_id: Mapped[int] = mapped_column(ForeignKey("agricultor.id"))
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedade.id"))
    servico_id: Mapped[int] = mapped_column(ForeignKey("servico.id"))
    operador_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    
    # CORREÇÃO: Definimos todos os relacionamentos aqui, usando backref.
    # Isto simplifica os outros modelos e resolve o erro de inicialização.
    agricultor: Mapped["Agricultor"] = relationship(backref="solicitacoes")
    propriedade: Mapped["Propriedade"] = relationship(backref="solicitacoes")
    servico: Mapped["Servico"] = relationship(backref="solicitacoes")
    operador: Mapped["Usuario"] = relationship(backref="solicitacoes_operadas")

    
