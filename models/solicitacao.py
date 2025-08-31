from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from helpers.database import db

class Solicitacao(db.Model):
    __tablename__ = 'solicitacao'

    id: Mapped[int] = mapped_column(primary_key=True)
    data_solicitacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_execucao: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Pendente')
    
    agricultor_id: Mapped[int] = mapped_column(ForeignKey('agricultor.id'), nullable=False)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey('propriedade.id'), nullable=False)
    servico_id: Mapped[int] = mapped_column(ForeignKey('servico.id'), nullable=False)
    operador_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'), nullable=True)

    # Relacionamentos
    agricultor: Mapped["Agricultor"] = relationship(back_populates="solicitacoes")
    propriedade: Mapped["Propriedade"] = relationship(back_populates="solicitacoes")
    servico: Mapped["Servico"] = relationship(back_populates="solicitacoes")
    operador: Mapped["Usuario"] = relationship(back_populates="solicitacoes_atendidas")