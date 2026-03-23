# Orcamento IA - MVP Full Stack

Migração do app legado em Streamlit para arquitetura SaaS com:
- Frontend: Next.js (`apps/web`)
- Backend: FastAPI (`apps/api`)
- Worker assíncrono: Celery + Redis
- Banco: PostgreSQL (em dev também pode usar SQLite)
- Núcleo preservado: `core/` (matching semântico + regras + escrita Excel)

## 1) Pré-requisitos

Para execução local sem Docker:
- Python 3.11+ e `pip`
- Node.js 20+ e `npm`
- Redis
- PostgreSQL 16+ (ou SQLite para dev rápido)

Para execução via Docker:
- Docker Desktop + Docker Compose

## 2) Estrutura do repositório

- `app.py`: interface Streamlit legada (continua funcional).
- `core/`: lógica central preservada (domínio + IA + Excel I/O).
- `apps/api/`: API FastAPI, serviços, rotas e worker Celery.
- `apps/web/`: frontend Next.js com fluxo real integrado.
- `docs/`: contrato de API, ADR e roadmap MVP.

## 3) Configuração de ambiente

### API
1. Copie `apps/api/.env.example` para `apps/api/.env`.
2. Ajuste as variáveis principais:
- `DATABASE_URL`
- `REDIS_URL`
- `CELERY_TASK_ALWAYS_EAGER`
- `STORAGE_DIR`
- `CORS_ORIGINS`

### Web
1. Copie `apps/web/.env.example` para `apps/web/.env.local`.
2. Ajuste:
- `NEXT_PUBLIC_API_BASE_URL` (ex.: `http://localhost:8000/api/v1`)

## 4) Rodar localmente sem Docker

### 4.1 Backend API
```bash
cd apps/api
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.2 Worker Celery
Em outro terminal:
```bash
cd apps/api
celery -A worker worker --loglevel=info
```

### 4.3 Frontend Next.js
Em outro terminal:
```bash
cd apps/web
npm install
npm run dev
```

### 4.4 URLs
- Web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- API base: `http://localhost:8000/api/v1`

## 5) Rodar com Docker

```bash
docker compose up --build
```

Serviços iniciados:
- `web` (3000)
- `api` (8000)
- `worker`
- `postgres` (5432)
- `redis` (6379)

## 6) Como testar o fluxo completo (E2E)

1. Acesse `http://localhost:3000/processing/new`.
2. Faça upload dos dois arquivos (`base` e `destino`).
3. Selecione abas e linhas de cabeçalho.
4. Clique em **Carregar colunas**.
5. Defina:
- coluna textual da base
- coluna de busca da destino
- mapeamentos base -> destino
- `score_minimo` e `top_k_candidatos`
6. Clique em **Criar job**.
7. Acompanhe o progresso na própria tela ou em `http://localhost:3000/history`.
8. Ao concluir, clique em **Baixar resultado**.

## 7) Endpoints principais

- `POST /api/v1/files/upload?kind=base|destino`
- `GET /api/v1/files/{file_id}/inspect?header_row=1`
- `GET /api/v1/files/{file_id}/sheet?sheet_name=...&header_row=1`
- `POST /api/v1/jobs`
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/jobs/{job_id}/result/download`

## 8) Modo de autenticação atual (MVP)

No momento a API usa autenticação MVP por headers:
- `x-user-id` (obrigatório)
- `x-user-email` (opcional)

O frontend já envia esses headers automaticamente em modo demo. A integração Clerk/JWT fica para a próxima etapa.

## 9) Limitações atuais do MVP

- Autenticação real com Clerk ainda não ativada (modo demo por header).
- Billing Stripe está apenas preparado (rotas placeholder).
- Não há migrações Alembic ainda (tabelas são criadas no boot da API).
- Storage em S3/R2 não ativado por padrão (usa filesystem local).
- Suite de testes ainda inicial (regras básicas do `core`).

## 10) Legado Streamlit

Se quiser continuar usando a interface antiga:
```bash
pip install -r requirements.txt
streamlit run app.py
```

O `app.py` agora consome o `core`, preservando a lógica funcional principal.

