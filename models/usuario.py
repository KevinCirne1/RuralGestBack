from helpers.database import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    perfil: Mapped[str] = mapped_column(String(50), nullable=False)
