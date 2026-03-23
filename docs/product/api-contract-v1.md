# API v1 (MVP)

Base path: `/api/v1`

## Auth
- `POST /auth/session/verify`

## Files
- `POST /files/upload?kind=base|destino`
- `GET /files/{file_id}/inspect?header_row=1`
- `GET /files/{file_id}/sheet?sheet_name=...&header_row=1`

## Jobs
- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/result`
- `GET /jobs/{job_id}/result/download`

## Billing (placeholder)
- `GET /billing/plans`
- `POST /billing/webhook/stripe`
