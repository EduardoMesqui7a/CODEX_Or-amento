# ADR 0001 - Stack principal do produto

## Status
Aceito

## Contexto
O produto precisa preservar o motor Python de matching com Excel, entregar UX SaaS premium e escalar para jobs assíncronos.

## Decisão
- Frontend: Next.js (App Router) + TypeScript.
- Backend: FastAPI.
- Processamento: Celery + Redis.
- Banco: PostgreSQL.
- Storage: S3 compatível em produção e storage local no dev.

## Consequências
- Reaproveitamento máximo da lógica atual em Python.
- Menor esforço para evoluir para autenticação e billing.
- Separação clara entre UX e domínio.

