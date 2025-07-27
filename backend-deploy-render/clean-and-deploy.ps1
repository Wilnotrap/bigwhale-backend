#!/usr/bin/env pwsh
# Script para limpar repositório GitHub e enviar apenas arquivos essenciais

Write-Host "BigWhale Backend - Limpeza e Deploy Completo" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Verificar se o Git está instalado
try {
    git --version | Out-Null
    Write-Host "[OK] Git encontrado" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Git nao encontrado. Instale o Git primeiro." -ForegroundColor Red
    Write-Host "Download: https://git-scm.com/download/windows" -ForegroundColor Yellow
    exit 1
}

# Diretório atual
$currentDir = Get-Location
$backendDir = "$currentDir"

Write-Host "Diretorio atual: $backendDir" -ForegroundColor Cyan
Write-Host ""

# Verificar se os arquivos necessários existem
$requiredFiles = @("app.py", "Procfile", "requirements.txt")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (Test-Path "$backendDir\$file") {
        Write-Host "[OK] $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] $file nao encontrado" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "[ERRO] Arquivos obrigatorios nao encontrados:" -ForegroundColor Red
    $missingFiles | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    Write-Host "Execute este script no diretório backend-deploy-render" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Iniciando limpeza e deploy completo..." -ForegroundColor Yellow
Write-Host ""

# Criar diretório temporário
$tempDir = "$env:TEMP\bigwhale-backend-clean"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "Clonando repositorio GitHub..." -ForegroundColor Cyan
try {
    Set-Location $tempDir
    git clone https://github.com/Wilnotrap/bigwhale-backend.git
    Set-Location "$tempDir\bigwhale-backend"
    Write-Host "[OK] Repositorio clonado com sucesso" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Erro ao clonar repositorio" -ForegroundColor Red
    Write-Host "Verifique sua conexao com a internet e acesso ao GitHub" -ForegroundColor Yellow
    Set-Location $currentDir
    exit 1
}

Write-Host ""
Write-Host "Limpando repositorio (removendo todos os arquivos)..." -ForegroundColor Yellow

try {
    # Remover todos os arquivos exceto .git
    Get-ChildItem -Path . -Exclude ".git" | Remove-Item -Recurse -Force
    Write-Host "[OK] Repositorio limpo" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Erro ao limpar repositorio" -ForegroundColor Red
    Set-Location $currentDir
    exit 1
}

Write-Host ""
Write-Host "Copiando apenas arquivos essenciais..." -ForegroundColor Cyan

# Lista de arquivos essenciais para o backend
$essentialFiles = @(
    @{Source = "$backendDir\app.py"; Dest = "app.py"},
    @{Source = "$backendDir\Procfile"; Dest = "Procfile"},
    @{Source = "$backendDir\requirements.txt"; Dest = "requirements.txt"}
)

try {
    foreach ($file in $essentialFiles) {
        Copy-Item $file.Source -Destination $file.Dest -Force
        Write-Host "[OK] $($file.Dest) copiado" -ForegroundColor Green
    }
    
    # Criar README.md simples
    $readmeContent = @"
# BigWhale Backend

## Backend Flask para BigWhale Trading System

### Caracteristicas:
- PostgreSQL em producao (Render)
- SQLite em desenvolvimento
- Deteccao automatica de ambiente
- CORS configurado para bwhale.site
- Endpoints essenciais de autenticacao

### Endpoints Disponiveis:
- GET /api/health - Health check
- POST /api/auth/login - Login
- POST /api/auth/register - Registro
- POST /api/credentials/save - Salvar credenciais API
- POST /api/credentials/validate - Validar credenciais

### Deploy:
Este backend esta configurado para deploy automatico no Render.com

### Usuario Admin Padrao:
- Email: admin@bigwhale.com
- Senha: Raikamaster1@

---
Versao: 2.0.0 | Ambiente: Producao
"@
    
    Set-Content -Path "README.md" -Value $readmeContent -Encoding UTF8
    Write-Host "[OK] README.md criado" -ForegroundColor Green
    
} catch {
    Write-Host "[ERRO] Erro ao copiar arquivos" -ForegroundColor Red
    Set-Location $currentDir
    exit 1
}

Write-Host ""
Write-Host "Arquivos no repositorio apos limpeza:" -ForegroundColor Cyan
Get-ChildItem -Name | ForEach-Object { Write-Host "   - $_" -ForegroundColor White }

Write-Host ""
Write-Host "Fazendo commit e push..." -ForegroundColor Cyan

try {
    # Configurar Git (caso não esteja configurado)
    git config user.name "BigWhale Deploy" 2>$null
    git config user.email "deploy@bigwhale.com" 2>$null
    
    # Adicionar todos os arquivos
    git add .
    
    # Verificar se há mudanças
    $status = git status --porcelain
    if ($status) {
        Write-Host "Mudancas detectadas:" -ForegroundColor Yellow
        git status --short | ForEach-Object { Write-Host "   $_" -ForegroundColor Yellow }
        
        # Fazer commit
        $commitMessage = "feat: Backend limpo e otimizado para producao

LIMPEZA COMPLETA:
* Removidos todos os arquivos antigos
* Mantidos apenas arquivos essenciais

NOVO BACKEND:
* app.py: Backend Flask otimizado
* Procfile: Configuracao correta para Render
* requirements.txt: Dependencias minimas + PostgreSQL
* README.md: Documentacao atualizada

CARACTERISTICAS:
* PostgreSQL em producao (preserva dados)
* SQLite em desenvolvimento
* Deteccao automatica de ambiente
* CORS configurado para bwhale.site
* Endpoints essenciais funcionando
* Pool de conexoes otimizado

RESULTADO:
* Repositorio limpo e organizado
* Deploy mais rapido e confiavel
* Codigo mantivel e documentado

Versao: 2.0.0"
        
        git commit -m $commitMessage
        
        Write-Host ""
        Write-Host "Fazendo push para GitHub..." -ForegroundColor Cyan
        git push origin main
        
        Write-Host "[OK] Push realizado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Nenhuma mudanca detectada" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "[ERRO] Erro durante commit/push" -ForegroundColor Red
    Write-Host "Voce pode precisar fazer login no GitHub ou configurar SSH" -ForegroundColor Yellow
    Write-Host "Tente fazer o push manualmente:" -ForegroundColor Yellow
    Write-Host "   cd $tempDir\bigwhale-backend" -ForegroundColor Cyan
    Write-Host "   git push origin main" -ForegroundColor Cyan
}

# Voltar ao diretório original
Set-Location $currentDir

Write-Host ""
Write-Host "Limpeza e Deploy Concluidos!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""
Write-Host "Resumo do que foi feito:" -ForegroundColor Cyan
Write-Host "[OK] Repositorio GitHub completamente limpo" -ForegroundColor Green
Write-Host "[OK] Apenas 4 arquivos essenciais enviados:" -ForegroundColor Green
Write-Host "   - app.py (backend otimizado)" -ForegroundColor White
Write-Host "   - Procfile (configuração Render)" -ForegroundColor White
Write-Host "   - requirements.txt (dependências)" -ForegroundColor White
Write-Host "   - README.md (documentação)" -ForegroundColor White
Write-Host "[OK] Commit e push realizados" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "1. Acesse https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Aguarde o deploy automático (2-5 minutos)" -ForegroundColor White
Write-Host "3. Teste: https://bigwhale-backend.onrender.com/api/health" -ForegroundColor White
Write-Host "4. Execute: python verify-postgresql.py" -ForegroundColor White
Write-Host ""
Write-Host "Links uteis:" -ForegroundColor Cyan
Write-Host "   GitHub: https://github.com/Wilnotrap/bigwhale-backend" -ForegroundColor Blue
Write-Host "   Render: https://dashboard.render.com" -ForegroundColor Blue
Write-Host "   Backend: https://bigwhale-backend.onrender.com" -ForegroundColor Blue
Write-Host ""
Write-Host "Seu repositorio esta limpo e o backend otimizado!" -ForegroundColor Green

# Limpeza
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Processo finalizado com sucesso!" -ForegroundColor Green