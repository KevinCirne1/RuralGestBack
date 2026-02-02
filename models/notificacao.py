from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
# A única importação externa necessária aqui é o banco de dados
from helpers.database import db 

class Notificacao(db.Model):
    __tablename__ = 'notificacao'

    id: Mapped[int] = mapped_column(primary_key=True)
    # Garanta que 'usuario.id' está correto (nome da tabela no banco)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'), nullable=False)
    
    mensagem: Mapped[str] = mapped_column(String(255), nullable=False)
    lida: Mapped[bool] = mapped_column(Boolean, default=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __init__(self, usuario_id: int, mensagem: str):
        self.usuario_id = usuario_id
        self.mensagem = mensagem

    def to_json(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "mensagem": self.mensagem,
            "lida": self.lida,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None
        }