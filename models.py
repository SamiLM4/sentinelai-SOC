# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
from database import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, index=True)       # ex: "login", "acesso", "requisicao"
    usuario = Column(String, index=True, nullable=True)
    ip = Column(String, index=True, nullable=True)
    sucesso = Column(Boolean, nullable=True)
    detalhes = Column(JSON, nullable=True)  # guarda qualquer dado extra específico do tipo
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class Incidente(Base):
    __tablename__ = "incidentes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, index=True)          # ex: "brute_force"
    severidade = Column(String)                # "baixa", "media", "alta", "critica"
    ip = Column(String, index=True, nullable=True)
    usuario = Column(String, index=True, nullable=True)
    descricao = Column(String)
    evidencias = Column(JSON, nullable=True)   # ex: lista dos eventos que geraram o incidente
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="aberto")
    analise_ia = Column(String, nullable=True)
    analisado_em = Column(DateTime(timezone=True), nullable=True)