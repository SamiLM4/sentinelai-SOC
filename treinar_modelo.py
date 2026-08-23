import json
# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
# pyrefly: ignore [missing-import]
import joblib

with open("dataset_normal.json") as f:
    eventos = json.load(f)

df = pd.DataFrame(eventos)

# codificação cíclica da hora
df["hora_sin"] = np.sin(2 * np.pi * df["hora"] / 24)
df["hora_cos"] = np.cos(2 * np.pi * df["hora"] / 24)

features = df[["hora_sin", "hora_cos", "dia_semana"]]

modelo = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42,
)
modelo.fit(features)

joblib.dump(modelo, "modelo_anomalia.pkl")
print("Modelo treinado e salvo em modelo_anomalia.pkl")