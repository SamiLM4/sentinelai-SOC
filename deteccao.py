from datetime import datetime, timedelta, timezone
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
import models
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import joblib

_modelo_anomalia = joblib.load("modelo_anomalia.pkl")

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

    incidente_existente = (
        db.query(models.Incidente)
        .filter(
            models.Incidente.tipo == "brute_force",
            models.Incidente.ip == evento.ip,
            models.Incidente.criado_em >= limite_tempo,
        )
        .first()
    )
    if incidente_existente:
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

def verificar_login_anomalo(evento: models.Evento, db: Session):
    if evento.tipo != "login" or evento.sucesso is not True or not evento.usuario:
        return None

    ips_anteriores = (
        db.query(models.Evento.ip)
        .filter(
            models.Evento.tipo == "login",
            models.Evento.sucesso == True,
            models.Evento.usuario == evento.usuario,
            models.Evento.id != evento.id,
        )
        .distinct()
        .all()
    )
    ips_anteriores = {ip for (ip,) in ips_anteriores if ip}

    if not ips_anteriores:
        return None

    if evento.ip in ips_anteriores:
        return None

    incidente = models.Incidente(
        tipo="login_anomalo",
        severidade="media",
        ip=evento.ip,
        usuario=evento.usuario,
        descricao=(
            f"Login bem-sucedido do usuário {evento.usuario} a partir de um IP "
            f"nunca utilizado antes ({evento.ip})"
        ),
        evidencias={"ips_conhecidos": list(ips_anteriores), "eventos_ids": [evento.id]},
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente

LIMITE_REQUISICOES = 30
JANELA_SEGUNDOS = 10

def verificar_api_abuse(evento: models.Evento, db: Session):
    if evento.tipo != "requisicao" or not evento.ip:
        return None

    limite_tempo = datetime.now(timezone.utc) - timedelta(seconds=JANELA_SEGUNDOS)

    requisicoes_recentes = (
        db.query(models.Evento)
        .filter(
            models.Evento.tipo == "requisicao",
            models.Evento.ip == evento.ip,
            models.Evento.criado_em >= limite_tempo,
        )
        .all()
    )

    if len(requisicoes_recentes) < LIMITE_REQUISICOES:
        return None

    incidente_existente = (
        db.query(models.Incidente)
        .filter(
            models.Incidente.tipo == "api_abuse",
            models.Incidente.ip == evento.ip,
            models.Incidente.criado_em >= limite_tempo,
        )
        .first()
    )
    if incidente_existente:
        return None

    incidente = models.Incidente(
        tipo="api_abuse",
        severidade="alta",
        ip=evento.ip,
        usuario=evento.usuario,
        descricao=(
            f"{len(requisicoes_recentes)} requisições do IP {evento.ip} "
            f"nos últimos {JANELA_SEGUNDOS} segundos"
        ),
        evidencias={"eventos_ids": [e.id for e in requisicoes_recentes]},
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente

RECURSOS_SENSIVEIS = ["/admin", "/financeiro", "/rh"]
JANELA_ACESSO_MINUTOS = 10

def verificar_acesso_sensivel(evento: models.Evento, db: Session):
    if evento.tipo != "acesso" or not evento.detalhes:
        return None

    recurso = evento.detalhes.get("recurso")
    if not recurso or not any(recurso.startswith(p) for p in RECURSOS_SENSIVEIS):
        return None

    limite_tempo = datetime.now(timezone.utc) - timedelta(minutes=JANELA_ACESSO_MINUTOS)

    incidente_existente = (
        db.query(models.Incidente)
        .filter(
            models.Incidente.tipo == "acesso_sensivel",
            models.Incidente.usuario == evento.usuario,
            models.Incidente.criado_em >= limite_tempo,
        )
        .first()
    )
    if incidente_existente:
        return None

    incidente = models.Incidente(
        tipo="acesso_sensivel",
        severidade="alta",
        ip=evento.ip,
        usuario=evento.usuario,
        descricao=(
            f"Usuário {evento.usuario} acessou o recurso sensível {recurso}"
        ),
        evidencias={"eventos_ids": [evento.id], "recurso": recurso},
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente

# ML

LIMIAR_ANOMALIA = -0.05

def verificar_comportamento_anomalo(evento: models.Evento, db: Session):
    if evento.tipo != "login" or evento.sucesso is not True:
        return None

    hora = evento.criado_em.hour
    dia_semana = evento.criado_em.weekday()

    hora_sin = np.sin(2 * np.pi * hora / 24)
    hora_cos = np.cos(2 * np.pi * hora / 24)

    features = pd.DataFrame(
        [[hora_sin, hora_cos, dia_semana]],
        columns=["hora_sin", "hora_cos", "dia_semana"],
    )
    score = _modelo_anomalia.decision_function(features)[0]

    if score > LIMIAR_ANOMALIA:
        return None

    incidente = models.Incidente(
        tipo="comportamento_anomalo_ml",
        severidade="media",
        ip=evento.ip,
        usuario=evento.usuario,
        descricao=(
            f"Login do usuário {evento.usuario} às {hora}h "
            f"apresenta padrão fora do comportamento habitual (score ML: {score:.3f})"
        ),
        evidencias={"eventos_ids": [evento.id], "anomaly_score": float(score)},
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente