# pyrefly: ignore [missing-import]
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class EventoCreate(BaseModel):
    tipo: str
    usuario: Optional[str] = None
    ip: Optional[str] = None
    sucesso: Optional[bool] = None
    detalhes: Optional[dict[str, Any]] = None

class EventoResponse(EventoCreate):
    id: int
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)

class IncidenteResponse(BaseModel):
    id: int
    tipo: str
    severidade: str
    ip: Optional[str] = None
    usuario: Optional[str] = None
    descricao: str
    evidencias: Optional[dict[str, Any]] = None
    criado_em: datetime
    status: str = "aberto"
    analise_ia: Optional[str] = None
    analisado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)