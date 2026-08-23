import random
from datetime import datetime, timedelta

USUARIOS = [f"user{i}" for i in range(1, 21)]
IP_POR_USUARIO = {u: f"192.168.1.{random.randint(2, 254)}" for u in USUARIOS}

def gerar_eventos_normais(quantidade=2000):
    eventos = []
    inicio = datetime(2026, 1, 1)

    for _ in range(quantidade):
        usuario = random.choice(USUARIOS)
        # horário de expediente: concentração entre 8h e 18h
        hora = int(random.gauss(13, 3))
        hora = max(0, min(23, hora))
        dia = random.randint(0, 89)
        timestamp = inicio + timedelta(days=dia, hours=hora, minutes=random.randint(0, 59))

        eventos.append({
            "usuario": usuario,
            "ip": IP_POR_USUARIO[usuario],
            "hora": hora,
            "dia_semana": timestamp.weekday(),
            "timestamp": timestamp.isoformat(),
        })

    return eventos

if __name__ == "__main__":
    import json
    eventos = gerar_eventos_normais()
    with open("dataset_normal.json", "w") as f:
        json.dump(eventos, f, indent=2)
    print(f"{len(eventos)} eventos gerados em dataset_normal.json")