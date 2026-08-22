# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def raiz():
    return {"status": "SentinelAI no ar"}

@app.post("/eventos", response_model=schemas.EventoResponse)
def criar_evento(evento: schemas.EventoCreate, db: Session = Depends(get_db)):
    novo_evento = models.Evento(**evento.model_dump())
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)
    return novo_evento

@app.get("/eventos", response_model=list[schemas.EventoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(models.Evento).order_by(models.Evento.id.desc()).all()