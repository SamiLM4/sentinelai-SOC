import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from openai import OpenAI

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_analise_incidente(incidente: dict, timeline: list[dict]) -> str:
    timeline_texto = "\n".join(
        f"- {e['criado_em']} | tipo={e['tipo']} usuario={e.get('usuario')} "
        f"ip={e.get('ip')} sucesso={e.get('sucesso')}"
        for e in timeline
    )

    prompt = f"""Você é um analista de segurança (SOC) experiente.

Analise o incidente abaixo e escreva uma análise curta e objetiva em português, com:
1. Resumo do que aconteceu (2-3 frases)
2. Por que isso é suspeito
3. Recomendação prática de ação

INCIDENTE:
Tipo: {incidente['tipo']}
Severidade: {incidente['severidade']}
Descrição: {incidente['descricao']}
IP: {incidente.get('ip')}
Usuário: {incidente.get('usuario')}

TIMELINE DE EVENTOS:
{timeline_texto}
"""

    resposta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    return resposta.choices[0].message.content