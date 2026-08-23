from datetime import datetime, timedelta, timezone
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
import models

LIMITE_FALHAS = 5
JANELA_MINUTOS = 2

def verificar_brute_force(evento: models.Evento, db: Session):
    if evento.tipo != "login" or evento.sucesso is not False:
        return None

    limite_tempo = datetime.now(timezone.utc) - timedelta(minutes=JANELA_MINUTOS)

    falhas_recentes = (
        db.query(models.Evento)
        .filter(
            models.Evento.tipo == "login",
            models.Evento.sucesso == False,
            models.Evento.ip == evento.ip,
            models.Evento.criado_em >= limite_tempo,
        )
        .all()
    )

    if len(falhas_recentes) < LIMITE_FALHAS:
        return None

    incidente = models.Incidente(
        tipo="brute_force",
        severidade="alta",
        ip=evento.ip,
        usuario=evento.usuario,
        descricao=(
            f"{len(falhas_recentes)} tentativas de login falhadas "
            f"do IP {evento.ip} nos últimos {JANELA_MINUTOS} minutos"
        ),
        evidencias={"eventos_ids": [e.id for e in falhas_recentes]},
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente