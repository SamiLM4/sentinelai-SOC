# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from security import verificar_api_key

from deteccao import (
    verificar_brute_force,
    verificar_login_anomalo,
    verificar_api_abuse,
    verificar_acesso_sensivel,
    verificar_comportamento_anomalo,
)

import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def raiz():
    return {"status": "SentinelAI no ar"}

@app.post("/eventos", response_model=schemas.EventoResponse)
def criar_evento(
    evento: schemas.EventoCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verificar_api_key)
):
    novo_evento = models.Evento(**evento.model_dump())
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)

    verificar_brute_force(novo_evento, db)
    verificar_login_anomalo(novo_evento, db)
    verificar_api_abuse(novo_evento, db)
    verificar_acesso_sensivel(novo_evento, db)
    verificar_comportamento_anomalo(novo_evento, db)

    return novo_evento

@app.get("/eventos", response_model=list[schemas.EventoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(models.Evento).order_by(models.Evento.id.desc()).all()

@app.get("/incidentes", response_model=list[schemas.IncidenteResponse])
def listar_incidentes(db: Session = Depends(get_db)):
    return db.query(models.Incidente).order_by(models.Incidente.id.desc()).all()

@app.get("/incidentes/{incidente_id}")
def detalhar_incidente(incidente_id: int, db: Session = Depends(get_db)):
    incidente = db.query(models.Incidente).filter(models.Incidente.id == incidente_id).first()
    if not incidente:
        return {"erro": "Incidente não encontrado"}

    eventos_ids = (incidente.evidencias or {}).get("eventos_ids", [])
    timeline = []
    if eventos_ids:
        timeline = (
            db.query(models.Evento)
            .filter(models.Evento.id.in_(eventos_ids))
            .order_by(models.Evento.criado_em.asc())
            .all()
        )

    return {
        "incidente": schemas.IncidenteResponse.model_validate(incidente),
        "timeline": [schemas.EventoResponse.model_validate(e) for e in timeline],
    }