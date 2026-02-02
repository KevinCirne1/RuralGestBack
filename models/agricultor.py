from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from helpers.database import db

# Importamos Usuario apenas para tipagem, se necessário, ou usamos string "Usuario"
# from models.usuario import Usuario 

class Agricultor(db.Model):
    __tablename__ = 'agricultor'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    cpf: Mapped[str] = mapped_column(String(20), unique=True, nullable=True) # CPF pode ser nulo em testes
    comunidade: Mapped[str] = mapped_column(String(100))
    contato: Mapped[str] = mapped_column(String(20))
    data_atualizacao_cadastro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- A PONTE QUE FALTAVA ---
    # Cria uma coluna para guardar o ID do login
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    
    # Cria o relacionamento para o Python entender
    usuario = relationship("Usuario", backref="agricultor_perfil")