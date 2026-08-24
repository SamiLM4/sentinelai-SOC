# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func as sql_func

from database import engine, Base, get_db
from security import verificar_api_key
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException

from datetime import datetime, timezone

from ia import gerar_analise_incidente

from deteccao import (
    verificar_brute_force,
    verificar_login_anomalo,
    verificar_api_abuse,
    verificar_acesso_sensivel,
    verificar_comportamento_anomalo,
)

import models
import schemas
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
def criar_tabelas():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sentinelai-dashboard-ten.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.patch("/incidentes/{incidente_id}/status", response_model=schemas.IncidenteResponse)
def atualizar_status_incidente(
    incidente_id: int,
    novo_status: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verificar_api_key),
):
    incidente = db.query(models.Incidente).filter(models.Incidente.id == incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente não encontrado")

    status_validos = ["aberto", "investigando", "resolvido", "falso_positivo"]
    if novo_status not in status_validos:
        raise HTTPException(status_code=400, detail=f"Status deve ser um de: {status_validos}")

    incidente.status = novo_status
    db.commit()
    db.refresh(incidente)
    return incidente

@app.get("/incidentes/{incidente_id}/analise")
def analisar_incidente(
    incidente_id: int,
    forcar: bool = False,
    db: Session = Depends(get_db),
    api_key: str = Depends(verificar_api_key),
):
    incidente = db.query(models.Incidente).filter(models.Incidente.id == incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente não encontrado")

    if incidente.analise_ia and not forcar:
        return {
            "incidente_id": incidente_id,
            "analise": incidente.analise_ia,
            "cache": True,
            "analisado_em": incidente.analisado_em,
        }

    eventos_ids = (incidente.evidencias or {}).get("eventos_ids", [])
    timeline = []
    if eventos_ids:
        timeline = (
            db.query(models.Evento)
            .filter(models.Evento.id.in_(eventos_ids))
            .order_by(models.Evento.criado_em.asc())
            .all()
        )

    incidente_dict = schemas.IncidenteResponse.model_validate(incidente).model_dump(mode="json")
    timeline_dict = [schemas.EventoResponse.model_validate(e).model_dump(mode="json") for e in timeline]

    analise = gerar_analise_incidente(incidente_dict, timeline_dict)

    incidente.analise_ia = analise
    incidente.analisado_em = datetime.now(timezone.utc)
    db.commit()

    return {
        "incidente_id": incidente_id,
        "analise": analise,
        "cache": False,
        "analisado_em": incidente.analisado_em,
    }

@app.get("/metricas")
def obter_metricas(db: Session = Depends(get_db)):
    total_eventos = db.query(models.Evento).count()
    total_incidentes = db.query(models.Incidente).count()
    incidentes_abertos = db.query(models.Incidente).filter(models.Incidente.status == "aberto").count()
    total_usuarios = db.query(sql_func.count(sql_func.distinct(models.Evento.usuario))).scalar()
    total_ips = db.query(sql_func.count(sql_func.distinct(models.Evento.ip))).scalar()

    return {
        "total_eventos": total_eventos,
        "total_incidentes": total_incidentes,
        "incidentes_abertos": incidentes_abertos,
        "total_usuarios": total_usuarios,
        "total_ips": total_ips,
    }