from __future__ import annotations
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from helpers.database import db
from helpers.application import bcrypt

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(50), nullable=False)
    
    solicitacoes_atendidas: Mapped[List["Solicitacao"]] = relationship(back_populates="operador")

    def __init__(self, nome, login, senha, perfil='tecnico'):
        self.nome = nome
        self.login = login
        self.senha = senha
        self.perfil = perfil

    def verificar_senha(self, senha_texto_plano):
        return bcrypt.check_password_hash(self.senha, senha_texto_plano)
