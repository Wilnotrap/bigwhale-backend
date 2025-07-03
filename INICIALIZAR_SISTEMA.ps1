# Script PowerShell para inicializar o sistema Bitget

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    INICIALIZANDO SISTEMA BITGET" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Função para verificar se um comando existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Verificar se Python está instalado
Write-Host "[VERIFICAÇÃO] Verificando Python..." -ForegroundColor Yellow
if (-not (Test-Command "python")) {
    Write-Host "❌ ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python em: https://python.org" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green

# Navegar para o diretório backend
Write-Host "\n[1/4] Navegando para o diretório backend..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ ERRO: Diretório backend não encontrado!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Set-Location $backendPath
Write-Host "✅ Diretório backend acessado" -ForegroundColor Green

# Corrigir banco de dados
Write-Host "\n[2/4] Corrigindo banco de dados..." -ForegroundColor Yellow
try {
    python fix_sistema.py
    Write-Host "✅ Banco de dados corrigido com sucesso" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO: Falha ao corrigir banco de dados" -ForegroundColor Red
    Write-Host "Tente executar manualmente: python fix_sistema.py" -ForegroundColor Red
    Read-Host "Pressione Enter para continuar mesmo assim"
}

# Iniciar backend
Write-Host "\n[3/4] Iniciando backend..." -ForegroundColor Yellow
Write-Host "Backend será iniciado em uma nova janela..." -ForegroundColor Cyan

try {
    Start-Process -FilePath "python" -ArgumentList "app.py" -WindowStyle Normal
    Write-Host "✅ Backend iniciado" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO: Falha ao iniciar backend" -ForegroundColor Red
    Write-Host "Tente executar manualmente: python app.py" -ForegroundColor Red
}

# Aguardar inicialização
Write-Host "\n[4/4] Aguardando 5 segundos para o backend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar se o backend está rodando
Write-Host "\n[VERIFICAÇÃO] Testando conexão com backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/test" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Backend está respondendo!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend pode não estar rodando ainda" -ForegroundColor Yellow
    Write-Host "Aguarde alguns segundos e tente acessar: http://localhost:5000" -ForegroundColor Yellow
}

# Informações finais
Write-Host "\n========================================" -ForegroundColor Cyan
Write-Host "       SISTEMA INICIALIZADO!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Backend: http://localhost:5000" -ForegroundColor Green
Write-Host "🌐 Frontend: Execute 'npm start' na pasta frontend" -ForegroundColor Green
Write-Host ""
Write-Host "🔑 CREDENCIAIS DE TESTE:" -ForegroundColor Yellow
Write-Host "   - admin@teste.com / 123456 (Admin)" -ForegroundColor White
Write-Host "   - user@teste.com / 123456 (Usuário)" -ForegroundColor White
Write-Host "   - teste@teste.com / 123456 (Teste)" -ForegroundColor White
Write-Host ""
Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "   1. Abra outro terminal" -ForegroundColor White
Write-Host "   2. Navegue para a pasta 'frontend'" -ForegroundColor White
Write-Host "   3. Execute: npm start" -ForegroundColor White
Write-Host "   4. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host ""
Read-Host "Pressione Enter para finalizar"