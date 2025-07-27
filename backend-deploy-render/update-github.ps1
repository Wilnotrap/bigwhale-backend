#!/usr/bin/env pwsh
# Script para atualizar o repositório GitHub com o backend corrigido

Write-Host "🚀 BigWhale Backend - Atualizador GitHub" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Verificar se o Git está instalado
try {
    git --version | Out-Null
    Write-Host "✅ Git encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Git não encontrado. Instale o Git primeiro." -ForegroundColor Red
    Write-Host "Download: https://git-scm.com/download/windows" -ForegroundColor Yellow
    exit 1
}

# Diretório atual
$currentDir = Get-Location
$backendDir = "$currentDir"

Write-Host "📁 Diretório atual: $backendDir" -ForegroundColor Cyan
Write-Host ""

# Verificar se os arquivos necessários existem
$requiredFiles = @("app.py", "Procfile", "requirements.txt")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (Test-Path "$backendDir\$file") {
        Write-Host "✅ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file não encontrado" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Arquivos obrigatórios não encontrados:" -ForegroundColor Red
    $missingFiles | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    Write-Host "Execute este script no diretório backend-deploy-render" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🔄 Iniciando processo de atualização..." -ForegroundColor Yellow
Write-Host ""

# Criar diretório temporário
$tempDir = "$env:TEMP\bigwhale-backend-update"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "📥 Clonando repositório GitHub..." -ForegroundColor Cyan
try {
    Set-Location $tempDir
    git clone https://github.com/Wilnotrap/bigwhale-backend.git
    Set-Location "$tempDir\bigwhale-backend"
    Write-Host "✅ Repositório clonado com sucesso" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao clonar repositório" -ForegroundColor Red
    Write-Host "Verifique sua conexão com a internet e acesso ao GitHub" -ForegroundColor Yellow
    Set-Location $currentDir
    exit 1
}

Write-Host ""
Write-Host "📝 Copiando arquivos corrigidos..." -ForegroundColor Cyan

# Copiar arquivos
try {
    Copy-Item "$backendDir\app.py" -Destination "$tempDir\bigwhale-backend\app.py" -Force
    Copy-Item "$backendDir\Procfile" -Destination "$tempDir\bigwhale-backend\Procfile" -Force
    Copy-Item "$backendDir\requirements.txt" -Destination "$tempDir\bigwhale-backend\requirements.txt" -Force
    
    Write-Host "✅ app.py copiado" -ForegroundColor Green
    Write-Host "✅ Procfile copiado" -ForegroundColor Green
    Write-Host "✅ requirements.txt copiado" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao copiar arquivos" -ForegroundColor Red
    Set-Location $currentDir
    exit 1
}

Write-Host ""
Write-Host "📤 Fazendo commit e push..." -ForegroundColor Cyan

try {
    # Configurar Git (caso não esteja configurado)
    git config user.name "BigWhale Deploy" 2>$null
    git config user.email "deploy@bigwhale.com" 2>$null
    
    # Adicionar arquivos
    git add app.py Procfile requirements.txt
    
    # Verificar se há mudanças
    $changes = git diff --cached --name-only
    if ($changes) {
        Write-Host "📋 Arquivos modificados:" -ForegroundColor Yellow
        $changes | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
        
        # Fazer commit
        $commitMessage = "fix: Corrigir backend para deploy no Render com PostgreSQL

- Corrigir Procfile (app:application)
- Adicionar suporte completo ao PostgreSQL
- Preservar dados existentes no banco
- Adicionar psycopg2-binary para PostgreSQL
- Configurar detecção automática de ambiente
- Adicionar endpoints essenciais
- Configurar CORS para bwhale.site"
        
        git commit -m $commitMessage
        
        Write-Host ""
        Write-Host "🚀 Fazendo push para GitHub..." -ForegroundColor Cyan
        git push origin main
        
        Write-Host "✅ Push realizado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ Nenhuma mudança detectada" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Erro durante commit/push" -ForegroundColor Red
    Write-Host "Você pode precisar fazer login no GitHub ou configurar SSH" -ForegroundColor Yellow
    Write-Host "Tente fazer o push manualmente:" -ForegroundColor Yellow
    Write-Host "   cd $tempDir\bigwhale-backend" -ForegroundColor Cyan
    Write-Host "   git push origin main" -ForegroundColor Cyan
}

# Voltar ao diretório original
Set-Location $currentDir

Write-Host ""
Write-Host "🎉 Processo concluído!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Acesse https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Encontre o serviço 'bigwhale-backend'" -ForegroundColor White
Write-Host "3. Aguarde o deploy automático (2-5 minutos)" -ForegroundColor White
Write-Host "4. Teste: https://bigwhale-backend.onrender.com/api/health" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Links úteis:" -ForegroundColor Cyan
Write-Host "   GitHub: https://github.com/Wilnotrap/bigwhale-backend" -ForegroundColor Blue
Write-Host "   Render: https://dashboard.render.com" -ForegroundColor Blue
Write-Host "   Backend: https://bigwhale-backend.onrender.com" -ForegroundColor Blue
Write-Host ""
Write-Host "✨ Seu backend deve estar funcionando em alguns minutos!" -ForegroundColor Green

# Limpeza
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}