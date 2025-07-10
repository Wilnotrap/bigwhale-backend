# Script PowerShell para executar o servidor Bitget
# Execução direta sem dependências do terminal do IDE

$ErrorActionPreference = "Stop"

# Definir diretório do projeto
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 BITGET TRADING - SERVIDOR FLASK" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar arquivos necessários
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$ServerScript = Join-Path $ProjectDir "backend\start_server_simple.py"

Write-Host "📁 Diretório: $ProjectDir" -ForegroundColor Yellow
Write-Host "🔍 Verificando arquivos..." -ForegroundColor Yellow

if (-not (Test-Path $VenvPython)) {
    Write-Host "❌ Python do ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "📍 Esperado em: $VenvPython" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

if (-not (Test-Path $ServerScript)) {
    Write-Host "❌ Arquivo do servidor não encontrado!" -ForegroundColor Red
    Write-Host "📍 Esperado em: $ServerScript" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "✅ Ambiente virtual encontrado" -ForegroundColor Green
Write-Host "✅ Servidor encontrado" -ForegroundColor Green
Write-Host ""

Write-Host "🔄 Iniciando servidor Flask..." -ForegroundColor Yellow
Write-Host "🌐 URL Principal: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📊 Health Check: http://localhost:5000/health" -ForegroundColor Cyan
Write-Host "📋 Dashboard: http://localhost:5000/api/dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Para parar o servidor, pressione Ctrl+C" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Executar o servidor
    & $VenvPython $ServerScript
}
catch {
    Write-Host "❌ Erro ao executar servidor: $_" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}
finally {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "🛑 Servidor finalizado" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
}

Read-Host "Pressione Enter para sair"