from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from helpers.database import db

class Veiculo(db.Model):
    __tablename__ = 'veiculo'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)  # Ex: Trator John Deere
    placa: Mapped[str] = mapped_column(String(20), nullable=True)   # Ex: KKK-9999
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)   # Ex: Trator, Caminhão
    status: Mapped[str] = mapped_column(String(20), default='DISPONIVEL', nullable=False) # DISPONIVEL, EM_USO, MANUTENCAO

    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "placa": self.placa,
            "tipo": self.tipo,
            "status": self.status
        }