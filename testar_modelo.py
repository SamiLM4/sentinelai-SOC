# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import joblib

modelo = joblib.load("modelo_anomalia.pkl")

print(f"{'hora':>5} {'dia':>5} {'score':>10} {'anomalo?':>10}")
for hora in range(24):
    for dia_semana in [1, 6]:  # terça (típico) e domingo (atípico)
        hora_sin = np.sin(2 * np.pi * hora / 24)
        hora_cos = np.cos(2 * np.pi * hora / 24)
        score = modelo.decision_function([[hora_sin, hora_cos, dia_semana]])[0]
        anomalo = "SIM" if score < -0.05 else ""
        print(f"{hora:>5} {dia_semana:>5} {score:>10.3f} {anomalo:>10}")