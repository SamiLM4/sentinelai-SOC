import requests
import time

API_URL = "https://sentinelai-api-48b3.onrender.com"
API_KEY = "uma-chave-bem-dificil-de-adivinhar-123"  # a mesma que está configurada no Render

HEADERS = {"X-API-Key": API_KEY}


def enviar(evento):
    resposta = requests.post(f"{API_URL}/eventos", headers=HEADERS, json=evento)
    print(evento["tipo"], "->", resposta.status_code)


print("1. Simulando brute force...")
for _ in range(6):
    enviar({"tipo": "login", "usuario": "carlos.souza", "ip": "203.0.113.10", "sucesso": False})

print("2. Simulando login anomalo...")
enviar({"tipo": "login", "usuario": "ana.lima", "ip": "192.168.1.50", "sucesso": True})
enviar({"tipo": "login", "usuario": "ana.lima", "ip": "45.33.12.199", "sucesso": True})

print("3. Simulando acesso sensivel...")
enviar({
    "tipo": "acesso",
    "usuario": "pedro.alves",
    "ip": "192.168.1.20",
    "detalhes": {"recurso": "/financeiro/folha-pagamento"},
})

print("4. Simulando api abuse...")
for _ in range(31):
    enviar({"tipo": "requisicao", "ip": "198.51.100.77", "sucesso": True})

print("Concluido! Confira o dashboard.")