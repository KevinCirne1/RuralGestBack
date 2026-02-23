from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from helpers.database import db

class Auditoria(db.Model):
    __tablename__ = 'auditoria'

    id: Mapped[int] = mapped_column(primary_key=True)
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Quem fez a ação? (Pode ser Null se for uma ação do sistema)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'), nullable=True)
    login_usuario: Mapped[str] = mapped_column(String(100), nullable=True) # Guardamos o nome caso o usuário seja deletado depois
    
    acao: Mapped[str] = mapped_column(String(50), nullable=False) # Ex: "CRIAR", "EXCLUIR", "VALIDAR"
    tabela_afetada: Mapped[str] = mapped_column(String(50), nullable=False) # Ex: "Solicitacao", "Agricultor"
    registro_id: Mapped[int] = mapped_column(db.Integer, nullable=True) # O ID do item mexido
    
    detalhes: Mapped[str] = mapped_column(Text, nullable=True) # Ex: "Mudou status de Pendente para Aprovada"

    usuario: Mapped["Usuario"] = relationship("Usuario")

    def __init__(self, acao, tabela, registro_id, usuario_id=None, login=None, detalhes=None):
        self.acao = acao
        self.tabela_afetada = tabela
        self.registro_id = registro_id
        self.usuario_id = usuario_id
        self.login_usuario = login
        self.detalhes = detalhes
        self.data_hora = datetime.now()