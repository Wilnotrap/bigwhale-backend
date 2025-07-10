#!/usr/bin/env pwsh
# 🔧 Script de Correção dos Problemas de Deploy
# Nautilus Automação - Fix Deployment Issues

Write-Host "🔧 CORREÇÃO DOS PROBLEMAS DE DEPLOY - NAUTILUS AUTOMAÇÃO" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "frontend" -PathType Container)) {
    Write-Host "❌ Erro: Execute este script na pasta raiz do projeto" -ForegroundColor Red
    exit 1
}

# 1. CORRIGIR ARQUIVO .HTACCESS DA HOSTINGER
Write-Host "📝 1. Corrigindo arquivo .htaccess da Hostinger..." -ForegroundColor Yellow

$htaccessContent = @'
Options -MultiViews
RewriteEngine On

# Handle Angular and React requests
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.html [QSA,L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# Content Security Policy - Corrigido para permitir Google Fonts e software de segurança
Header always set Content-Security-Policy "default-src ''self''; script-src ''self'' ''unsafe-inline'' ''unsafe-eval'' https://cdn.jsdelivr.net https://unpkg.com https://*.kaspersky-labs.com https://*.avast.com https://*.avg.com https://*.norton.com https://*.bitdefender.com https://*.mcafee.com; style-src ''self'' ''unsafe-inline'' https://fonts.googleapis.com https://cdn.jsdelivr.net; font-src ''self'' https://fonts.gstatic.com https://cdn.jsdelivr.net; img-src ''self'' data: https:; connect-src ''self'' https://bigwhale-backend.onrender.com https://*.kaspersky-labs.com https://*.avast.com https://*.avg.com https://*.norton.com https://*.bitdefender.com https://*.mcafee.com; frame-ancestors ''none''; base-uri ''self''; form-action ''self'';"

# CORS Headers for API communication
Header always set Access-Control-Allow-Origin "https://bwhale.site"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With"
Header always set Access-Control-Allow-Credentials "true"

# Cache static assets
<filesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
  ExpiresActive On
  ExpiresDefault "access plus 1 month"
  Header append Cache-Control "public"
</filesMatch>

# Compress files
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/plain
  AddOutputFilterByType DEFLATE text/html
  AddOutputFilterByType DEFLATE text/xml
  AddOutputFilterByType DEFLATE text/css
  AddOutputFilterByType DEFLATE application/xml
  AddOutputFilterByType DEFLATE application/xhtml+xml
  AddOutputFilterByType DEFLATE application/rss+xml
  AddOutputFilterByType DEFLATE application/javascript
  AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>
'@

$htaccessContent | Out-File -FilePath "frontend-deploy-hostinger\.htaccess" -Encoding UTF8
Write-Host "   ✅ Arquivo .htaccess corrigido" -ForegroundColor Green

# 2. VERIFICAR E CORRIGIR CONFIGURAÇÃO DA API
Write-Host "📝 2. Verificando configuração da API..." -ForegroundColor Yellow

$apiConfigPath = "frontend\src\config\api.js"
if (Test-Path $apiConfigPath) {
    $apiConfig = Get-Content $apiConfigPath -Raw
    if ($apiConfig -match "bigwhale-backend.onrender.com") {
        Write-Host "   ✅ URL do backend está correta" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  URL do backend pode estar incorreta" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   ❌ Arquivo de configuração da API não encontrado" -ForegroundColor Red
}

# 3. VERIFICAR ARQUIVO .ENV.PRODUCTION
Write-Host "📝 3. Verificando arquivo .env.production..." -ForegroundColor Yellow

$envProdPath = "frontend\.env.production"
if (Test-Path $envProdPath) {
    $envContent = Get-Content $envProdPath -Raw
    if ($envContent -match "bigwhale-backend.onrender.com") {
        Write-Host "   ✅ Arquivo .env.production está correto" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  Corrigindo arquivo .env.production..." -ForegroundColor Yellow
        
        $newEnvContent = @'
REACT_APP_API_URL=https://bigwhale-backend.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_DOMAIN=bwhale.site
REACT_APP_SECURE_MODE=true
REACT_APP_SSL_ENABLED=true
GENERATE_SOURCEMAP=false
'@
        $newEnvContent | Out-File -FilePath $envProdPath -Encoding UTF8
        Write-Host "   ✅ Arquivo .env.production corrigido" -ForegroundColor Green
    }
}
else {
    Write-Host "   ❌ Arquivo .env.production não encontrado" -ForegroundColor Red
}

# 4. TESTAR CONECTIVIDADE COM O BACKEND
Write-Host "📝 4. Testando conectividade com o backend..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "https://bigwhale-backend.onrender.com/api/health" -Method GET -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend está respondendo corretamente" -ForegroundColor Green
        $healthData = $response.Content | ConvertFrom-Json
        Write-Host "   📊 Status: $($healthData.status)" -ForegroundColor Cyan
    }
    else {
        Write-Host "   ⚠️  Backend respondeu com status: $($response.StatusCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ❌ Erro ao conectar com o backend: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   💡 Verifique se o backend está ativo no Render" -ForegroundColor Yellow
}

# 5. REBUILD DO FRONTEND
Write-Host "📝 5. Fazendo rebuild do frontend..." -ForegroundColor Yellow

Set-Location "frontend"

# Limpar cache do npm
Write-Host "   🧹 Limpando cache..." -ForegroundColor Cyan
npm cache clean --force 2>$null

# Instalar dependências
Write-Host "   📦 Instalando dependências..." -ForegroundColor Cyan
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Dependências instaladas" -ForegroundColor Green
    
    # Build de produção
    Write-Host "   🏗️  Fazendo build de produção..." -ForegroundColor Cyan
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Build concluído com sucesso" -ForegroundColor Green
        
        # Copiar arquivos para o diretório de deploy
        Write-Host "   📁 Copiando arquivos para deploy..." -ForegroundColor Cyan
        
        Set-Location ".."
        
        # Limpar diretório de deploy
        if (Test-Path "frontend-deploy-hostinger\static") {
            Remove-Item "frontend-deploy-hostinger\static" -Recurse -Force
        }
        
        # Copiar novos arquivos
        Copy-Item "frontend\build\*" "frontend-deploy-hostinger\" -Recurse -Force
        
        Write-Host "   ✅ Arquivos copiados para frontend-deploy-hostinger" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Erro no build do frontend" -ForegroundColor Red
        Set-Location ".."
        exit 1
    }
}
else {
    Write-Host "   ❌ Erro ao instalar dependências" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Set-Location ".."

# 6. CRIAR ARQUIVO DE INSTRUÇÕES
Write-Host "📝 6. Criando arquivo de instruções..." -ForegroundColor Yellow

$instructionsContent = @'
🚀 INSTRUÇÕES DE DEPLOY CORRIGIDO - NAUTILUS AUTOMAÇÃO
=======================================================

✅ PROBLEMAS CORRIGIDOS:
1. Content Security Policy atualizada para permitir Google Fonts
2. Adicionado suporte para software de segurança (Kaspersky, Avast, etc.)
3. Headers CORS configurados corretamente
4. Configuração da API verificada
5. Build do frontend atualizado

📋 PRÓXIMOS PASSOS:

1. UPLOAD NA HOSTINGER:
   - Acesse o Gerenciador de Arquivos da Hostinger
   - Navegue até public_html/
   - Faça upload de TODOS os arquivos da pasta "frontend-deploy-hostinger"
   - Substitua os arquivos existentes

2. VERIFICAR PERMISSÕES:
   - Certifique-se de que o arquivo .htaccess foi enviado
   - Verifique se as permissões estão corretas (644 para arquivos, 755 para pastas)

3. TESTAR O SITE:
   - Acesse https://bwhale.site/login
   - Teste o login com: admin@bigwhale.com / Raikamaster1@
   - Verifique se não há mais erros no console

4. LIMPAR CACHE:
   - Limpe o cache do navegador
   - Teste em modo incógnito

🔧 SE AINDA HOUVER PROBLEMAS:
1. Verifique se o backend está ativo no Render
2. Teste a conectividade usando o arquivo test_connectivity.html
3. Verifique os logs do Render para erros no backend

📞 SUPORTE:
- Frontend: Hostinger (bwhale.site)
- Backend: Render (bigwhale-backend.onrender.com)
- Banco: SQLite (local no backend)
'@

$instructionsContent | Out-File -FilePath "INSTRUCOES_DEPLOY_CORRIGIDO.txt" -Encoding UTF8
Write-Host "   ✅ Arquivo de instruções criado: INSTRUCOES_DEPLOY_CORRIGIDO.txt" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 CORREÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Arquivos prontos para upload na pasta: frontend-deploy-hostinger" -ForegroundColor Cyan
Write-Host "📋 Leia o arquivo: INSTRUCOES_DEPLOY_CORRIGIDO.txt" -ForegroundColor Cyan
Write-Host "🧪 Teste a conectividade com: test_connectivity.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Próximo passo: Faça upload dos arquivos na Hostinger" -ForegroundColor Yellow
Write-Host ""