# Script para rodar o QAgent localmente no Windows
# Verifica dependências e inicia o bot

Write-Host "Iniciando QAgent..." -ForegroundColor Cyan

# Verifica se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "ERRO: Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "DICA: Copie o arquivo .env.example para .env e configure suas chaves."
    exit 1
}

# Verifica se o ambiente virtual existe (opcional, mas recomendado)
if (Test-Path "venv") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}

# Verifica e instala dependências se necessário (opcional para rodar rápido)
# pip install -r requirements.txt

# Inicia o bot
python main.py
