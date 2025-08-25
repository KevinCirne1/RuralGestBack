from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey
from datetime import datetime

class Solicitacao(db.Model):
    __tablename__ = 'solicitacao'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_solicitacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data_execucao: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Pendente')

    agricultor_id: Mapped[int] = mapped_column(ForeignKey("agricultor.id"), nullable=False)
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedade.id"), nullable=False)
    servico_id: Mapped[int] = mapped_column(ForeignKey("servico.id"), nullable=False)
    operador_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=True)

    agricultor: Mapped["Agricultor"] = relationship(backref="solicitacoes")
    propriedade: Mapped["Propriedade"] = relationship(backref="solicitacoes")
    servico: Mapped["Servico"] = relationship(backref="solicitacoes")
    operador: Mapped["Usuario"] = relationship(backref="solicitacoes_atendidas")

