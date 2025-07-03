# Script PowerShell para executar o sistema Bitget

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    EXECUTANDO SISTEMA BITGET" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Função para verificar se um comando existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Verificar pré-requisitos
Write-Host "[VERIFICAÇÃO] Verificando pré-requisitos..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Host "❌ ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python em: https://python.org" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

if (-not (Test-Command "npm")) {
    Write-Host "❌ ERRO: Node.js/npm não encontrado!" -ForegroundColor Red
    Write-Host "Instale Node.js em: https://nodejs.org" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "✅ Python e Node.js encontrados" -ForegroundColor Green

# Definir caminhos
$projectRoot = $PSScriptRoot
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"

# [1/3] Iniciar Backend
Write-Host "\n[1/3] Iniciando Backend..." -ForegroundColor Yellow

if (-not (Test-Path $backendPath)) {
    Write-Host "❌ ERRO: Diretório backend não encontrado!" -ForegroundColor Red
    exit 1
}

Set-Location $backendPath

# Corrigir banco de dados
Write-Host "Corrigindo banco de dados..." -ForegroundColor Cyan
try {
    python fix_sistema.py
    Write-Host "✅ Banco de dados corrigido" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Aviso: Erro ao corrigir banco, continuando..." -ForegroundColor Yellow
}

# Iniciar backend em nova janela
Write-Host "Iniciando servidor Flask..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "app.py" -WindowStyle Normal

# [2/3] Aguardar backend
Write-Host "\n[2/3] Aguardando backend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# [3/3] Iniciar Frontend
Write-Host "\n[3/3] Iniciando Frontend..." -ForegroundColor Yellow

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ ERRO: Diretório frontend não encontrado!" -ForegroundColor Red
    exit 1
}

Set-Location $frontendPath

# Verificar se node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependências do npm..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERRO: Falha ao instalar dependências" -ForegroundColor Red
        Read-Host "Pressione Enter para continuar mesmo assim"
    } else {
        Write-Host "✅ Dependências instaladas" -ForegroundColor Green
    }
}

# Iniciar frontend em nova janela
Write-Host "Iniciando servidor React..." -ForegroundColor Cyan
Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Normal

# Informações finais
Write-Host "\n========================================" -ForegroundColor Green
Write-Host "       SISTEMA INICIADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "👤 CREDENCIAIS DE TESTE:" -ForegroundColor Yellow
Write-Host "   • admin@teste.com / 123456 (Admin)" -ForegroundColor White
Write-Host "   • user@teste.com / 123456 (Usuário)" -ForegroundColor White
Write-Host "   • teste@teste.com / 123456 (Teste)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Dica: Aguarde alguns segundos para os servidores iniciarem completamente" -ForegroundColor Yellow
Write-Host ""
Read-Host "Pressione Enter para fechar este script"