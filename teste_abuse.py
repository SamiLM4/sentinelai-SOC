# venv\Scripts\Activate.ps1

import requests

URL = "http://127.0.0.1:8080/eventos"
HEADERS = {"X-API-Key": "uma-chave-bem-dificil-de-adivinhar-123"}

for i in range(35):
    resposta = requests.post(URL, headers=HEADERS, json={
        "tipo": "requisicao",
        "ip": "198.51.100.20",
        "usuario": None,
        "sucesso": True
    })
    print(i, resposta.status_code)