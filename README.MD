# 🛡️ SentinelAI

![CI](https://github.com/SamiLM4/sentinelai-SOC/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Plataforma experimental de SOC (Security Operations Center) que combina detecção baseada em regras, detecção de anomalias por Machine Learning e IA generativa para investigação e explicação de incidentes de segurança.

**🔗 [Dashboard ao vivo](https://sentinelai-dashboard-ten.vercel.app)** · **📄 [Documentação da API](https://sentinelai-api-48b3.onrender.com/docs)**

> Nota: a API roda em plano gratuito e pode levar ~30-60s para "acordar" caso esteja ociosa há alguns minutos.

---

## 📌 Sobre o projeto

O SentinelAI simula, em pequena escala, o que uma plataforma de SOC faz numa empresa real: recebe eventos de segurança (login, acesso a recursos, requisições de API), analisa esses eventos em tempo real e cria **incidentes** quando identifica comportamento suspeito. Cada incidente pode ser investigado através de uma timeline dos eventos que o geraram, e uma IA generativa gera uma análise explicando o que aconteceu, por que é suspeito, e qual ação tomar.

O projeto foi construído do zero como estudo prático de backend, machine learning aplicado e integração com IA generativa — cada fase abaixo foi desenvolvida, testada e documentada incrementalmente.

## 🧠 Detecções implementadas

| Detecção | Método | Descrição |
|---|---|---|
| 🔓 Brute Force | Regras | 5+ tentativas de login falhadas do mesmo IP em 2 minutos |
| 🌍 Login Anômalo | Regras | Login bem-sucedido de um IP nunca usado antes pelo usuário |
| 📡 API Abuse | Regras | 30+ requisições do mesmo IP em 10 segundos |
| 🔐 Acesso Sensível | Regras | Acesso a recursos administrativos/financeiros |
| 🤖 Comportamento Anômalo | Machine Learning (Isolation Forest) | Login em horário fora do padrão aprendido |

Toda detecção gera um incidente com evidências rastreáveis (os eventos exatos que motivaram o alerta) e pode ser investigada com uma explicação gerada por IA sob demanda.

## 🏗️ Arquitetura

```text
                         ┌─────────────┐
                         │   FastAPI   │
                         │    (API)    │
                         └──────┬──────┘
                                │
               Eventos          │
      (login/acesso/requisição) │
                                ▼
                  ┌─────────────┼─────────────┐
                  │             │             │
                  ▼             ▼             ▼
            ┌──────────┐  ┌────────────┐  ┌─────────────┐
            │  Regras  │  │ Isolation  │  │ PostgreSQL  │
            │ (4 tipos)│  │   Forest   │  │  (eventos)  │
            └────┬─────┘  └─────┬──────┘  └─────────────┘
                 │              │
                 └──────┬───────┘
                        ▼
                 ┌─────────────┐
                 │  Incidente  │
                 └──────┬──────┘
                        │
                 ┌──────┴──────┐
                 │             │
                 ▼             ▼
          ┌─────────────┐ ┌──────────────┐
          │  OpenAI API │ │  Dashboard   │
          │   (análise) │ │    (React)   │
          └─────────────┘ └──────────────┘
```



## 🛠️ Stack

| Camada | Tecnologias |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Banco de dados | PostgreSQL |
| Machine Learning | scikit-learn (Isolation Forest) |
| IA generativa | OpenAI API (gpt-4o-mini) |
| Frontend | React, TypeScript, Vite, React Router |
| Infraestrutura | Docker, Docker Compose |
| Testes | pytest |
| CI/CD | GitHub Actions |
| Deploy | Render (API + Postgres) · Vercel (dashboard) |

## 🚀 Como rodar localmente

### Pré-requisitos
- Docker Desktop
- Node.js (para o dashboard)

### Backend + banco de dados

```bash
git clone https://github.com/SamiLM4/sentinelai-SOC.git
cd sentinelai-SOC
cp .env.example .env  # preencha suas chaves
docker compose up -d --build
```

A API estará disponível em `http://localhost:8080`, com documentação interativa em `http://localhost:8080/docs`.

### Dashboard

```bash
git clone https://github.com/SamiLM4/sentinelai-dashboard.git
cd sentinelai-dashboard
npm install
npm run dev
```

Disponível em `http://localhost:5173`.

### Rodando os testes

```bash
python -m pytest -v
```

## 📡 Principais endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/eventos` | Recebe um novo evento (requer API Key) |
| `GET` | `/eventos` | Lista eventos |
| `GET` | `/incidentes` | Lista incidentes detectados |
| `GET` | `/incidentes/{id}` | Detalhe do incidente + timeline |
| `PATCH` | `/incidentes/{id}/status` | Atualiza status do incidente |
| `GET` | `/incidentes/{id}/analise` | Gera/retorna análise por IA (cacheada) |
| `GET` | `/metricas` | Métricas agregadas do sistema |

## 🗺️ Próximos passos

- [ ] Migrations com Alembic (hoje o schema é alterado manualmente)
- [ ] Mais features no modelo de ML (frequência de acessos, geolocalização de IP)
- [ ] Correlação de eventos entre múltiplas regras (grafo de incidentes)
- [ ] Autenticação de usuário no dashboard (hoje só a API é protegida)

## 📄 Licença

Este projeto é livre para fins de estudo e portfólio.