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
        evidencias={"ips_conhecidos": list(ips_anteriores), "evento_id": evento.id},
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
        evidencias={"evento_id": evento.id, "recurso": recurso},
    )
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente