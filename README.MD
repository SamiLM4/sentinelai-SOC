# 🛡️ SentinelAI

Plataforma experimental de SOC (Security Operations Center) que combina detecção baseada em regras, detecção de anomalias por Machine Learning e IA generativa para investigação e explicação de incidentes de segurança.

## O que o sistema faz

O SentinelAI recebe eventos de segurança (login, acesso a recursos, requisições de API), analisa esses eventos em tempo real usando regras e um modelo de Machine Learning, e cria **incidentes** quando identifica comportamento suspeito. Cada incidente pode ser investigado através de uma timeline dos eventos que o geraram, e uma IA generativa gera uma análise explicando o que aconteceu, por que é suspeito, e o que fazer a respeito.

## Detecções implementadas

| Detecção | Método | Descrição |
|---|---|---|
| Brute Force | Regras | 5+ tentativas de login falhadas do mesmo IP em 2 minutos |
| Login Anômalo | Regras | Login bem-sucedido de um IP nunca usado antes pelo usuário |
| API Abuse | Regras | 30+ requisições do mesmo IP em 10 segundos |
| Acesso Sensível | Regras | Acesso a recursos administrativos/financeiros |
| Comportamento Anômalo | Machine Learning (Isolation Forest) | Login em horário fora do padrão aprendido |

## Arquitetura
Eventos → API (FastAPI) → Regras + ML → Incidentes → IA (explicação) → Dashboard
↓
PostgreSQL

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Banco de dados**: PostgreSQL
- **Machine Learning**: scikit-learn (Isolation Forest)
- **IA generativa**: OpenAI API
- **Frontend**: React, TypeScript, Vite
- **Infraestrutura**: Docker, Docker Compose
- **Testes**: pytest

## Como rodar

### Pré-requisitos
- Docker Desktop
- Node.js (para o dashboard)

### Backend + banco de dados

```bash
git clone <url-do-seu-repo>
cd sentinelai
cp .env.example .env  # preencha suas chaves
docker compose up -d --build
```

A API estará disponível em `http://localhost:8080`, com documentação interativa em `http://localhost:8080/docs`.

### Dashboard

```bash
cd sentinelai-dashboard
npm install
npm run dev
```

Disponível em `http://localhost:5173`.

### Rodando os testes

```bash
python -m pytest -v
```

## Principais endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/eventos` | Recebe um novo evento (requer API Key) |
| GET | `/eventos` | Lista eventos |
| GET | `/incidentes` | Lista incidentes detectados |
| GET | `/incidentes/{id}` | Detalhe do incidente + timeline |
| PATCH | `/incidentes/{id}/status` | Atualiza status do incidente |
| GET | `/incidentes/{id}/analise` | Gera/retorna análise por IA |
| GET | `/metricas` | Métricas agregadas do sistema |

## Próximos passos

- Migrations com Alembic
- CI/CD com GitHub Actions
- Mais features no modelo de ML (frequência de acessos, geolocalização)