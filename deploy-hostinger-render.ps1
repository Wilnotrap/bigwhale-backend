# ========================================
# 🚀 BigWhale Deploy Script - Hostinger + Render
# ========================================

Write-Host "🚀 BigWhale Deploy Script - Hostinger + Render" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Configurações
$FRONTEND_DIR = "frontend"
$DEPLOY_DIR = "frontend-deploy-hostinger"
$BACKEND_URL = "https://bigwhale-backend.onrender.com"
$FRONTEND_URL = "https://bwhale.site"

# Função para verificar se um comando existe
function Test-Command {
    param($Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Verificar dependências
Write-Host "🔍 Verificando dependências..." -ForegroundColor Yellow

if (-not (Test-Command "npm")) {
    Write-Host "❌ Node.js/npm não encontrado. Instale o Node.js primeiro." -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "curl")) {
    Write-Host "❌ curl não encontrado. Instale o curl primeiro." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependências verificadas!" -ForegroundColor Green

# Testar Backend
Write-Host "🔍 Testando backend..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BACKEND_URL/api/health" -Method GET -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host "✅ Backend funcionando: $($response.message)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend com status: $($response.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro ao conectar com backend: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔄 Continuando com o deploy..." -ForegroundColor Yellow
}

# Navegar para diretório do frontend
if (-not (Test-Path $FRONTEND_DIR)) {
    Write-Host "❌ Diretório do frontend não encontrado: $FRONTEND_DIR" -ForegroundColor Red
    exit 1
}

Set-Location $FRONTEND_DIR

# Verificar se package.json existe
if (-not (Test-Path "package.json")) {
    Write-Host "❌ package.json não encontrado no diretório frontend" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
npm install --silent

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependências instaladas!" -ForegroundColor Green

# Criar arquivo .env.production
Write-Host "⚙️ Criando arquivo .env.production..." -ForegroundColor Yellow
$envContent = @"
REACT_APP_API_URL=https://bigwhale-backend.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_DOMAIN=https://bwhale.site
GENERATE_SOURCEMAP=false
CI=false

# Configurações de segurança
REACT_APP_ENABLE_SECURITY_LOGS=false
REACT_APP_ENABLE_CONSOLE_LOGS=false
REACT_APP_ENABLE_PERFORMANCE_MONITORING=true

# Configurações de API
REACT_APP_API_TIMEOUT=10000
REACT_APP_API_RETRY_ATTEMPTS=3
REACT_APP_API_RETRY_DELAY=1000

# Configurações de sessão
REACT_APP_SESSION_TIMEOUT=1800000
REACT_APP_SESSION_CHECK_INTERVAL=60000
REACT_APP_SESSION_WARNING_TIME=300000
"@

$envContent | Out-File -FilePath ".env.production" -Encoding UTF8
Write-Host "✅ Arquivo .env.production criado!" -ForegroundColor Green

# Build do frontend
Write-Host "🔨 Fazendo build do frontend..." -ForegroundColor Yellow
npm run build:prod

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build do frontend" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build do frontend concluído!" -ForegroundColor Green

# Voltar para diretório raiz
Set-Location ..

# Criar diretório de deploy
if (Test-Path $DEPLOY_DIR) {
    Write-Host "🗑️ Removendo deploy anterior..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $DEPLOY_DIR
}

Write-Host "📁 Criando diretório de deploy..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $DEPLOY_DIR | Out-Null

# Copiar arquivos do build
Write-Host "📋 Copiando arquivos do build..." -ForegroundColor Yellow
Copy-Item -Path "$FRONTEND_DIR/build/*" -Destination $DEPLOY_DIR -Recurse

# Verificar se .htaccess está correto
$htaccessPath = "$DEPLOY_DIR/.htaccess"
if (Test-Path $htaccessPath) {
    Write-Host "✅ Arquivo .htaccess encontrado!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Arquivo .htaccess não encontrado, criando..." -ForegroundColor Yellow
    # Criar .htaccess com configurações corretas
    $htaccessContent = @"
RewriteEngine On

# Forçar HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Headers de Segurança
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# Content Security Policy - CORRIGIDO para permitir Google Fonts e Backend Render
Header set Content-Security-Policy "default-src 'self'; connect-src 'self' https://bigwhale-backend.onrender.com wss://bigwhale-backend.onrender.com ws://localhost:3000 https://*.kaspersky-labs.com https://*.avast.com https://*.avg.com https://*.norton.com https://*.mcafee.com https://*.bitdefender.com https://*.eset.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com; script-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data: https: blob:; media-src 'self' blob:; object-src 'none'; frame-src 'none';"

# CORS Headers para comunicação com backend
Header always set Access-Control-Allow-Origin "https://bigwhale-backend.onrender.com"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With, Accept, Origin, Cache-Control, X-API-KEY"
Header always set Access-Control-Allow-Credentials "true"

# Cache para assets estáticos
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
    Header append Cache-Control "public"
</FilesMatch>

# Roteamento para React (SPA)
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.html [L]

# Bloquear acesso a arquivos sensíveis
<FilesMatch "\.(env|log|ini|md|txt)$">
    Order allow,deny
    Deny from all
</FilesMatch>

# Compressão de arquivos
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
    AddOutputFilterByType DEFLATE application/json
</IfModule>
"@
    
    $htaccessContent | Out-File -FilePath $htaccessPath -Encoding UTF8
    Write-Host "✅ Arquivo .htaccess criado!" -ForegroundColor Green
}

# Criar arquivo de instruções
Write-Host "📝 Criando arquivo de instruções..." -ForegroundColor Yellow
$instructionsContent = @"
# 🚀 INSTRUÇÕES DE UPLOAD - BigWhale Hostinger

## 📁 Arquivos para Upload
Todos os arquivos da pasta '$DEPLOY_DIR' devem ser enviados para o diretório público da Hostinger.

## 🔧 Configurações Importantes
1. ✅ Arquivo .htaccess já está configurado
2. ✅ CSP configurado para permitir Google Fonts
3. ✅ CORS configurado para o backend Render
4. ✅ Build otimizado para produção

## 🧪 Testes Pós-Upload
1. Acessar: $FRONTEND_URL
2. Verificar se as fontes estão carregando
3. Testar login com: admin@bigwhale.com / Raikamaster1@
4. Verificar console do navegador para erros

## 📞 URLs Importantes
- Frontend: $FRONTEND_URL
- Backend: $BACKEND_URL
- Health Check: $BACKEND_URL/api/health

## 🔍 Troubleshooting
- Se houver erro de CORS, verificar se o backend está rodando
- Se as fontes não carregarem, verificar o CSP no .htaccess
- Se o login não funcionar, verificar cookies e sessão

Data do deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

$instructionsContent | Out-File -FilePath "$DEPLOY_DIR/INSTRUCOES_UPLOAD.txt" -Encoding UTF8

# Resumo final
Write-Host ""
Write-Host "🎉 DEPLOY PREPARADO COM SUCESSO!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "📁 Arquivos preparados em: $DEPLOY_DIR" -ForegroundColor Cyan
Write-Host "📝 Instruções: $DEPLOY_DIR/INSTRUCOES_UPLOAD.txt" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔄 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Fazer upload dos arquivos de '$DEPLOY_DIR' para a Hostinger" -ForegroundColor White
Write-Host "2. Verificar se o .htaccess foi aplicado corretamente" -ForegroundColor White
Write-Host "3. Testar o site em: $FRONTEND_URL" -ForegroundColor White
Write-Host "4. Verificar se não há erros no console do navegador" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Sistema pronto para produção!" -ForegroundColor Green

# Testar se o frontend está funcionando localmente
Write-Host "🔍 Testando build local..." -ForegroundColor Yellow
if (Test-Path "$DEPLOY_DIR/index.html") {
    Write-Host "✅ Build local criado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no build local" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 