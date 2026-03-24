$ErrorActionPreference = "Stop"

Write-Host "Subindo Orcamento IA em modo local rapido..." -ForegroundColor Cyan
docker compose up --build
