# 🚀 Script de Deploy Automatizado para GoDaddy
# Nautilus Automação - Deploy Script

Write-Host "🚀 Iniciando Deploy para GoDaddy - Nautilus Automação" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Yellow

# Configurações
$DOMAIN = Read-Host "Digite seu domínio (ex: seusite.com)"
$BUILD_DIR = "./frontend/build"
$DEPLOY_DIR = "./deploy-package"
$API_DIR = "./backend"

# Função para verificar se comando existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Verificar pré-requisitos
Write-Host "🔍 Verificando pré-requisitos..." -ForegroundColor Blue

if (-not (Test-Command "npm")) {
    Write-Host "❌ NPM não encontrado. Instale Node.js primeiro." -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "python")) {
    Write-Host "❌ Python não encontrado. Instale Python primeiro." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pré-requisitos OK" -ForegroundColor Green

# Limpar diretório de deploy anterior
if (Test-Path $DEPLOY_DIR) {
    Write-Host "🧹 Limpando deploy anterior..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $DEPLOY_DIR
}

# Criar estrutura de deploy
Write-Host "📁 Criando estrutura de deploy..." -ForegroundColor Blue
New-Item -ItemType Directory -Path $DEPLOY_DIR -Force | Out-Null
New-Item -ItemType Directory -Path "$DEPLOY_DIR/api" -Force | Out-Null
New-Item -ItemType Directory -Path "$DEPLOY_DIR/api/instance" -Force | Out-Null

# 1. BUILD DO FRONTEND
Write-Host "🔨 Fazendo build do frontend..." -ForegroundColor Blue
Set-Location "./frontend"

# Criar .env.production
$envProduction = @"
REACT_APP_API_URL=https://$DOMAIN/api
REACT_APP_ENVIRONMENT=production
REACT_APP_ENABLE_SECURITY_LOGS=false
GENERATE_SOURCEMAP=false
"@

$envProduction | Out-File -FilePath ".env.production" -Encoding UTF8
Write-Host "✅ Arquivo .env.production criado" -ForegroundColor Green

# Instalar dependências e fazer build
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências do frontend" -ForegroundColor Red
    exit 1
}

npm run build:secure
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build do frontend" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build do frontend concluído" -ForegroundColor Green

# Copiar arquivos do build para deploy
Copy-Item -Path "./build/*" -Destination "../$DEPLOY_DIR" -Recurse -Force
Write-Host "✅ Arquivos do frontend copiados" -ForegroundColor Green

Set-Location ".."

# 2. PREPARAR BACKEND
Write-Host "🐍 Preparando backend..." -ForegroundColor Blue

# Criar .env.production para backend
$backendEnv = @"
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(Get-Random -Minimum 100000000 -Maximum 999999999)_$(Get-Date -Format 'yyyyMMddHHmmss')
DATABASE_URL=sqlite:///instance/site.db
API_BASE_URL=https://$DOMAIN/api
CORS_ORIGINS=https://$DOMAIN
"@

$backendEnv | Out-File -FilePath "$DEPLOY_DIR/api/.env.production" -Encoding UTF8
Write-Host "✅ Arquivo .env.production do backend criado" -ForegroundColor Green

# Criar app.wsgi
$wsgiContent = @"
#!/usr/bin/python3
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, '/home/seuusuario/public_html/api/')

# Configurar variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

from app import app as application

if __name__ == "__main__":
    application.run()
"@

$wsgiContent | Out-File -FilePath "$DEPLOY_DIR/api/app.wsgi" -Encoding UTF8
Write-Host "✅ Arquivo app.wsgi criado" -ForegroundColor Green

# Criar requirements.txt otimizado
$requirements = @"
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Session==0.5.0
requests==2.31.0
APScheduler==3.10.4
gunicorn==21.2.0
python-dotenv==1.0.0
"@

$requirements | Out-File -FilePath "$DEPLOY_DIR/api/requirements.txt" -Encoding UTF8
Write-Host "✅ Arquivo requirements.txt criado" -ForegroundColor Green

# Copiar arquivos do backend
Copy-Item -Path "./backend/*" -Destination "$DEPLOY_DIR/api/" -Recurse -Force -Exclude @("__pycache__", "*.pyc", ".env", "venv")
Write-Host "✅ Arquivos do backend copiados" -ForegroundColor Green

# Copiar banco de dados se existir
if (Test-Path "./instance/site.db") {
    Copy-Item -Path "./instance/site.db" -Destination "$DEPLOY_DIR/api/instance/" -Force
    Write-Host "✅ Banco de dados copiado" -ForegroundColor Green
}

# 3. CRIAR ARQUIVOS .HTACCESS
Write-Host "⚙️ Criando arquivos .htaccess..." -ForegroundColor Blue

# .htaccess principal
$htaccessMain = @"
# Redirecionar HTTP para HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Headers de Segurança
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"

# Content Security Policy
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://$DOMAIN; font-src 'self'; object-src 'none'; media-src 'self'; frame-src 'none'"

# Roteamento para API
RewriteRule ^api/(.*)$ /api/app.wsgi/`$1 [QSA,L]

# Roteamento para React (SPA)
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api/
RewriteRule . /index.html [L]

# Compressão
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

# Cache
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>
"@

$htaccessMain | Out-File -FilePath "$DEPLOY_DIR/.htaccess" -Encoding UTF8
Write-Host "✅ .htaccess principal criado" -ForegroundColor Green

# .htaccess da API
$htaccessAPI = @"
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ app.wsgi/`$1 [QSA,L]

# Headers CORS
Header always set Access-Control-Allow-Origin "https://$DOMAIN"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization, X-CSRF-Token"
"@

$htaccessAPI | Out-File -FilePath "$DEPLOY_DIR/api/.htaccess" -Encoding UTF8
Write-Host "✅ .htaccess da API criado" -ForegroundColor Green

# 4. CRIAR ARQUIVO ZIP PARA UPLOAD
Write-Host "📦 Criando arquivo ZIP para upload..." -ForegroundColor Blue

$zipFile = "nautilus-deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"
Compress-Archive -Path "$DEPLOY_DIR/*" -DestinationPath $zipFile -Force

Write-Host "✅ Arquivo ZIP criado: $zipFile" -ForegroundColor Green

# 5. CRIAR INSTRUÇÕES DE DEPLOY
$instructions = @"
🚀 INSTRUÇÕES DE DEPLOY - NAUTILUS AUTOMAÇÃO
=============================================

📦 Arquivo gerado: $zipFile
🌐 Domínio configurado: $DOMAIN

📋 PRÓXIMOS PASSOS:

1. ACESSE O CPANEL DO GODADDY
   - Faça login em sua conta GoDaddy
   - Acesse o cPanel da sua hospedagem

2. BACKUP (IMPORTANTE!)
   - Faça backup dos arquivos atuais
   - cPanel → File Manager → Selecionar tudo → Compress

3. LIMPAR PUBLIC_HTML
   - cPanel → File Manager
   - Navegue até public_html/
   - Selecione todos os arquivos (exceto .well-known se existir)
   - Delete

4. UPLOAD DO PROJETO
   - No File Manager, navegue até public_html/
   - Clique em "Upload"
   - Selecione o arquivo: $zipFile
   - Aguarde o upload completar
   - Clique com botão direito no arquivo ZIP
   - Selecione "Extract"
   - Confirme a extração
   - Delete o arquivo ZIP após extração

5. CONFIGURAR PERMISSÕES
   - Selecione a pasta api/
   - Clique em "Permissions"
   - Defina como 755
   - Marque "Recurse into subdirectories"
   - Apply

6. INSTALAR DEPENDÊNCIAS PYTHON
   - cPanel → Terminal (se disponível) OU
   - cPanel → Python App (se disponível)
   - Execute: cd public_html/api && pip install -r requirements.txt

7. CONFIGURAR SSL
   - cPanel → SSL/TLS
   - Ative "Force HTTPS Redirect"
   - Instale certificado SSL (Let's Encrypt recomendado)

8. TESTAR A APLICAÇÃO
   - Acesse: https://$DOMAIN
   - Teste login e funcionalidades
   - Verifique: https://$DOMAIN/api/health

🔧 TROUBLESHOOTING:

- Erro 500: Verifique Error Logs no cPanel
- API não responde: Verifique permissões e dependências Python
- CORS Error: Verifique configuração de domínio

📞 SUPORTE:
- Documentação: Consulte DEPLOY_GODADDY_GUIDE.md
- GoDaddy: Suporte técnico 24/7

✅ CHECKLIST FINAL:
[ ] Backup realizado
[ ] Arquivos enviados
[ ] Permissões configuradas
[ ] Dependências instaladas
[ ] SSL ativado
[ ] Aplicação testada

🎉 Sucesso! Sua aplicação está no ar!
"@

$instructions | Out-File -FilePath "INSTRUCOES_DEPLOY.txt" -Encoding UTF8

# 6. RESUMO FINAL
Write-Host "" -ForegroundColor White
Write-Host "🎉 DEPLOY PREPARADO COM SUCESSO!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Yellow
Write-Host "📦 Arquivo ZIP: $zipFile" -ForegroundColor Cyan
Write-Host "📋 Instruções: INSTRUCOES_DEPLOY.txt" -ForegroundColor Cyan
Write-Host "🌐 Domínio: https://$DOMAIN" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Blue
Write-Host "1. Abra o arquivo INSTRUCOES_DEPLOY.txt" -ForegroundColor White
Write-Host "2. Faça upload do arquivo $zipFile no cPanel" -ForegroundColor White
Write-Host "3. Siga as instruções passo a passo" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "🚀 Boa sorte com o deploy!" -ForegroundColor Green

# Abrir pasta de deploy
Start-Process explorer.exe -ArgumentList (Get-Location).Path

# Pausar para o usuário ler
Read-Host "Pressione Enter para finalizar"