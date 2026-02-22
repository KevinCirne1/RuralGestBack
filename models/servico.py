from __future__ import annotations
from typing import List
from sqlalchemy import String, Float, Boolean # <--- ADICIONEI Boolean AQUI
from sqlalchemy.orm import Mapped, mapped_column, relationship
from helpers.database import db

class Servico(db.Model):
    __tablename__ = 'servico'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_servico: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=True)
    capacidade_hectares: Mapped[float] = mapped_column(Float, nullable=True)
    tipo_veiculo: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # NOVA COLUNA: Define se o serviço exige atribuição de funcionário
    # default=True garante que os serviços antigos continuem exigindo funcionário até você mudar
    requer_funcionario: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    solicitacoes: Mapped[List["Solicitacao"]] = relationship(back_populates="servico")