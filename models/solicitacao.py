from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, String, ForeignKey
from helpers.database import db

# Nota: Não importamos os outros models aqui no topo para evitar erro de ciclo (circular import)

class Solicitacao(db.Model):
    __tablename__ = 'solicitacao'

    id: Mapped[int] = mapped_column(primary_key=True)
    data_solicitacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data_execucao: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Pendente')
    motivo_recusa: Mapped[str] = mapped_column(String(255), nullable=True)

    # Chaves Estrangeiras
    agricultor_id: Mapped[int] = mapped_column(ForeignKey("agricultor.id"))
    propriedade_id: Mapped[int] = mapped_column(ForeignKey("propriedade.id"))
    servico_id: Mapped[int] = mapped_column(ForeignKey("servico.id"))
    
    # Campo para o Veículo
    veiculo_id: Mapped[int] = mapped_column(ForeignKey("veiculo.id"), nullable=True)

    # Operador (Quem atendeu/aprovou)
    operador_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    
    # --- RELACIONAMENTOS ---
    
    # Usamos backref simples aqui pois não temos conflito nas outras classes
    agricultor: Mapped["Agricultor"] = relationship(backref="solicitacoes")
    propriedade: Mapped["Propriedade"] = relationship(backref="solicitacoes")
    servico: Mapped["Servico"] = relationship(backref="solicitacoes")
    veiculo: Mapped["Veiculo"] = relationship(backref="solicitacoes")

    # --- CORREÇÃO DO ERRO AQUI ---
    # Usamos back_populates para casar com 'solicitacoes_atendidas' da classe Usuario
    operador: Mapped["Usuario"] = relationship(back_populates="solicitacoes_atendidas")

    def to_json(self):
        return {
            "id": self.id,
            "data_solicitacao": self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            "data_execucao": self.data_execucao.isoformat() if self.data_execucao else None,
            "status": self.status,
            "motivo_recusa": self.motivo_recusa,
            
            # Retorna o objeto completo (ou dict) para o frontend acessar sub-propriedades
            # Ex: sol.servico.tipo_veiculo
            "servico": self.servico.to_json() if self.servico else None,
            "servico_id": self.servico_id,

            "agricultor": self.agricultor.to_json() if self.agricultor else None,
            "agricultor_id": self.agricultor_id,

            "propriedade": self.propriedade.to_json() if self.propriedade else None,
            "propriedade_id": self.propriedade_id,

            "veiculo": self.veiculo.to_json() if self.veiculo else None,
            "veiculo_id": self.veiculo_id,

            # Opcional: Dados do operador que aprovou
            "operador": self.operador.nome if self.operador else None
        }