from security import API_KEY


def test_criar_evento_sem_api_key_retorna_erro(client):
    resposta = client.post("/eventos", json={
        "tipo": "login",
        "usuario": "teste",
        "ip": "1.1.1.1",
        "sucesso": True,
    })
    assert resposta.status_code in (401, 403)


def test_criar_evento_com_api_key_funciona(client):
    resposta = client.post(
        "/eventos",
        headers={"X-API-Key": API_KEY},
        json={
            "tipo": "login",
            "usuario": "teste",
            "ip": "1.1.1.1",
            "sucesso": True,
        },
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["tipo"] == "login"
    assert dados["usuario"] == "teste"
    assert "id" in dados


def test_listar_eventos_retorna_lista(client):
    client.post(
        "/eventos",
        headers={"X-API-Key": API_KEY},
        json={"tipo": "login", "usuario": "a", "ip": "1.1.1.1", "sucesso": True},
    )

    resposta = client.get("/eventos")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_brute_force_gera_incidente_apos_5_falhas(client):
    for _ in range(5):
        client.post(
            "/eventos",
            headers={"X-API-Key": API_KEY},
            json={"tipo": "login", "usuario": "vitima", "ip": "9.9.9.9", "sucesso": False},
        )

    incidentes = client.get("/incidentes").json()
    tipos = [i["tipo"] for i in incidentes]
    assert "brute_force" in tipos


def test_brute_force_nao_dispara_com_4_falhas(client):
    for _ in range(4):
        client.post(
            "/eventos",
            headers={"X-API-Key": API_KEY},
            json={"tipo": "login", "usuario": "vitima", "ip": "8.8.8.8", "sucesso": False},
        )

    incidentes = client.get("/incidentes").json()
    assert len(incidentes) == 0