# Orcamento IA - Modo Local Rapido

O projeto agora prioriza **execucao local rapida**:
- `web` em `localhost:3000`
- `api` em `localhost:8000`
- `SQLite + filesystem local`
- processamento inline na API

Esse modo recupera a experiencia de velocidade do fluxo antigo em Streamlit, mas preserva a interface web atual.

## Subida rapida com Docker

Prerequisito:
- Docker Desktop em execucao

Comando principal:

```powershell
docker compose up --build
```

Atalhos no Windows:

```powershell
.\scripts\start-local.ps1
```

ou

```bat
scripts\start-local.bat
```

## URLs locais

- Web: `http://localhost:3000`
- Tela principal: `http://localhost:3000/processing/new`
- API health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

## Como o modo local funciona

- os uploads vao para o storage local da API
- o banco padrao e `SQLite`
- o job roda na propria maquina
- nao ha dependencia obrigatoria de `Postgres`, `Redis` ou `worker`

Defaults locais:

- `DATABASE_URL=sqlite:///./local.db`
- `STORAGE_DIR=./storage`
- `CELERY_TASK_ALWAYS_EAGER=true`
- `CORS_ORIGINS=http://localhost:3000`
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1`

## Fluxo de uso

1. Abra `http://localhost:3000/processing/new`
2. Envie `base` e `planilha destino`
3. Selecione as abas
4. Clique em `Carregar colunas`
5. Ajuste mapeamentos
6. Clique em `Criar job`
7. Baixe o resultado final

## Modo completo opcional

Se voce quiser reproduzir uma stack mais proxima do SaaS, ainda existe um compose complementar com `Postgres + Redis + worker`:

```powershell
docker compose -f docker-compose.yml -f docker-compose.full.yml up --build
```

Esse modo nao e o caminho principal para uso individual local.

## Execucao sem Docker

### API

```powershell
cd apps/api
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Web

```powershell
cd apps/web
npm install
npm run dev
```

## Streamlit legado

O Streamlit continua disponivel como fallback:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Observacoes

- O site online continua existindo como demo e caminho de validacao remota.
- O modo local agora e o modo recomendado para arquivos grandes e uso rapido.
- A logica central do matching continua preservada em `core/`.
