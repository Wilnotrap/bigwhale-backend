# 🚀 Script de Deploy Automatizado para Hostinger
# Nautilus Automação - Deploy Script

Write-Host "🚀 Iniciando Deploy para Hostinger - Nautilus Automação" -ForegroundColor Green
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

Write-Host "✅ Pré-requisitos verificados" -ForegroundColor Green
Write-Host ""

# Limpar diretório de deploy anterior
Write-Host "🧹 Limpando deploy anterior..." -ForegroundColor Blue
if (Test-Path $DEPLOY_DIR) {
    Remove-Item -Path $DEPLOY_DIR -Recurse -Force
    Write-Host "   ✅ Diretório anterior removido" -ForegroundColor Green
}

# Criar estrutura de deploy
Write-Host "📁 Criando estrutura de deploy..." -ForegroundColor Blue
New-Item -ItemType Directory -Path $DEPLOY_DIR -Force | Out-Null
New-Item -ItemType Directory -Path "$DEPLOY_DIR/api" -Force | Out-Null
Write-Host "   ✅ Estrutura criada" -ForegroundColor Green
Write-Host ""

# Preparar Frontend
Write-Host "🎨 Preparando Frontend..." -ForegroundColor Blue
Set-Location "./frontend"

# Criar .env.production para o frontend
$frontendEnvContent = @"
REACT_APP_API_URL=https://$DOMAIN/api
REACT_APP_ENVIRONMENT=production
REACT_APP_DOMAIN=$DOMAIN
REACT_APP_SECURE_MODE=true
REACT_APP_SSL_ENABLED=true
GENERATE_SOURCEMAP=false
"@

Set-Content -Path ".env.production" -Value $frontendEnvContent
Write-Host "   ✅ .env.production criado" -ForegroundColor Green

# Build do frontend com configurações de segurança
Write-Host "   🔨 Executando build seguro..." -ForegroundColor Cyan
npm run build:secure
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build do frontend" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "   ✅ Build do frontend concluído" -ForegroundColor Green

# Copiar arquivos do build para deploy
Copy-Item -Path "./build/*" -Destination "../$DEPLOY_DIR/" -Recurse -Force
Write-Host "   ✅ Arquivos copiados para deploy" -ForegroundColor Green

Set-Location ".."
Write-Host ""

# Preparar Backend
Write-Host "🐍 Preparando Backend..." -ForegroundColor Blue

# Criar .env.production para o backend
$backendEnvContent = @"
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(Get-Random -Minimum 100000000 -Maximum 999999999)
DATABASE_URL=sqlite:///instance/site.db
CORS_ORIGINS=https://$DOMAIN
API_BASE_URL=https://$DOMAIN/api
FRONTEND_URL=https://$DOMAIN
SECURE_MODE=true
SSL_REQUIRED=true
HOSTINGER_MODE=true
"@

Set-Content -Path "$API_DIR/.env.production" -Value $backendEnvContent
Write-Host "   ✅ .env.production do backend criado" -ForegroundColor Green

# Criar app.wsgi para Hostinger
$wsgiContent = @"
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Importar a aplicação
from app import app as application

if __name__ == "__main__":
    application.run()
"@

Set-Content -Path "$API_DIR/app.wsgi" -Value $wsgiContent
Write-Host "   ✅ app.wsgi criado" -ForegroundColor Green

# Criar requirements.txt otimizado para Hostinger
$requirementsContent = @"
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Session==0.5.0
requests==2.31.0
websocket-client==1.6.4
SQLAlchemy==2.0.23
Werkzeug==2.3.7
python-dotenv==1.0.0
cryptography==41.0.7
PyJWT==2.8.0
"@

Set-Content -Path "$API_DIR/requirements.txt" -Value $requirementsContent
Write-Host "   ✅ requirements.txt otimizado criado" -ForegroundColor Green

# Copiar backend para deploy
Copy-Item -Path "$API_DIR/*" -Destination "$DEPLOY_DIR/api/" -Recurse -Force -Exclude @("__pycache__", "*.pyc", ".env", "venv", "logs/*")
Write-Host "   ✅ Backend copiado para deploy" -ForegroundColor Green
Write-Host ""

# Criar .htaccess principal (para frontend)
Write-Host "⚙️ Criando configurações..." -ForegroundColor Blue

$mainHtaccess = @"
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

# Cache para assets estáticos
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
    Header append Cache-Control "public"
</FilesMatch>

# Roteamento para React (SPA)
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api/
RewriteRule . /index.html [L]

# Bloquear acesso a arquivos sensíveis
<FilesMatch "\.(env|log|ini)$">
    Order allow,deny
    Deny from all
</FilesMatch>
"@

Set-Content -Path "$DEPLOY_DIR/.htaccess" -Value $mainHtaccess
Write-Host "   ✅ .htaccess principal criado" -ForegroundColor Green

# Criar .htaccess da API
$apiHtaccess = @"
RewriteEngine On

# Forçar HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Roteamento para Flask via WSGI
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ app.wsgi/`$1 [QSA,L]

# Headers CORS para Hostinger
Header always set Access-Control-Allow-Origin "https://$DOMAIN"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With"
Header always set Access-Control-Allow-Credentials "true"

# Headers de Segurança
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"

# Bloquear acesso a arquivos sensíveis
<FilesMatch "\.(env|log|ini|py)$">
    Order allow,deny
    Deny from all
</FilesMatch>

# Permitir apenas app.wsgi
<FilesMatch "app\.wsgi$">
    Order allow,deny
    Allow from all
</FilesMatch>
"@

Set-Content -Path "$DEPLOY_DIR/api/.htaccess" -Value $apiHtaccess
Write-Host "   ✅ .htaccess da API criado" -ForegroundColor Green
Write-Host ""

# Criar arquivo ZIP
Write-Host "📦 Criando pacote de deploy..." -ForegroundColor Blue
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipFile = "nautilus-deploy-$timestamp.zip"

Compress-Archive -Path "$DEPLOY_DIR/*" -DestinationPath $zipFile -Force
Write-Host "   ✅ Pacote criado: $zipFile" -ForegroundColor Green
Write-Host ""

# Criar instruções específicas para Hostinger
$instructions = @"
🚀 INSTRUÇÕES DE DEPLOY - NAUTILUS AUTOMAÇÃO (HOSTINGER)
=======================================================

📦 Arquivo gerado: $zipFile
🌐 Domínio configurado: $DOMAIN

📋 PRÓXIMOS PASSOS:

1. ACESSE O PAINEL HOSTINGER
   - Faça login em sua conta Hostinger
   - Acesse o hPanel (painel principal)
   - Ou acesse o cPanel se disponível

2. BACKUP (IMPORTANTE!)
   - Faça backup dos arquivos atuais
   - hPanel → Gerenciador de Arquivos → public_html
   - Selecione tudo → Compress → Baixe o backup

3. LIMPAR PUBLIC_HTML
   - Gerenciador de Arquivos → public_html/
   - Selecione todos os arquivos (exceto .well-known se existir)
   - Delete os arquivos antigos

4. UPLOAD DO ARQUIVO ZIP
   - No Gerenciador de Arquivos, clique em "Upload"
   - Selecione o arquivo: $zipFile
   - Aguarde o upload (limite: 256MB no hPanel)

5. EXTRAIR ARQUIVOS
   - Clique com botão direito no arquivo ZIP
   - Selecione "Extract" (Extrair)
   - Extrair para: public_html/
   - Confirme a extração

6. CONFIGURAR PERMISSÕES
   - Navegue até public_html/api/
   - Clique com botão direito na pasta "api"
   - Permissions → 755 (rwxr-xr-x)
   - Marque "Recurse into subdirectories"

7. CONFIGURAR PYTHON (se disponível)
   
   OPÇÃO A - VPS/Cloud com SSH:
   ```
   cd public_html/api
   pip install -r requirements.txt
   ```
   
   OPÇÃO B - Python App Manager:
   - hPanel → Python → Nova Aplicação
   - Diretório: public_html/api
   - Instalar dependências do requirements.txt
   
   OPÇÃO C - Hospedagem Compartilhada:
   - Verifique se Python está disponível
   - Entre em contato com suporte se necessário

8. ATIVAR SSL
   - hPanel → SSL → Ativar SSL gratuito
   - Aguarde ativação (até 24h)
   - Teste: https://$DOMAIN

9. TESTAR APLICAÇÃO
   - Frontend: https://$DOMAIN
   - API: https://$DOMAIN/api/health
   - Teste login e funcionalidades

🔧 TROUBLESHOOTING:

- Erro 500: Verifique Error Logs no hPanel
- API não responde: Confirme permissões e Python
- CORS Error: Verifique configuração de domínio
- SSL não funciona: Aguarde 24h ou contate suporte

📞 SUPORTE:
- Hostinger: Chat 24/7 no hPanel
- Documentação: DEPLOY_HOSTINGER_GUIDE.md
- Base de Conhecimento: support.hostinger.com

✅ CHECKLIST FINAL:
- [ ] Backup realizado
- [ ] Arquivo ZIP enviado e extraído
- [ ] Permissões configuradas (755 para api/)
- [ ] Python configurado (se disponível)
- [ ] SSL ativado
- [ ] Frontend funcionando (https://$DOMAIN)
- [ ] API respondendo (https://$DOMAIN/api/health)
- [ ] Login testado
- [ ] Logs verificados

🎉 SUCESSO!
Seu Nautilus Automação está rodando no Hostinger!

📱 URLs importantes:
- Site: https://$DOMAIN
- API: https://$DOMAIN/api
- Health: https://$DOMAIN/api/health

---
Deploy gerado em: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')
Hostinger Deploy Script v1.0 - Nautilus Automação
"@

Set-Content -Path "INSTRUCOES_DEPLOY_HOSTINGER.txt" -Value $instructions
Write-Host "📄 Instruções criadas: INSTRUCOES_DEPLOY_HOSTINGER.txt" -ForegroundColor Green
Write-Host ""

# Resumo final
Write-Host "🎉 Deploy preparado com sucesso!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Yellow
Write-Host "📦 Arquivo ZIP: $zipFile" -ForegroundColor Cyan
Write-Host "📄 Instruções: INSTRUCOES_DEPLOY_HOSTINGER.txt" -ForegroundColor Cyan
Write-Host "🌐 Domínio: $DOMAIN" -ForegroundColor Cyan
Write-Host "📚 Guia completo: DEPLOY_HOSTINGER_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Abra o arquivo INSTRUCOES_DEPLOY_HOSTINGER.txt" -ForegroundColor White
Write-Host "2. Acesse seu painel Hostinger (hPanel)" -ForegroundColor White
Write-Host "3. Siga as instruções passo a passo" -ForegroundColor White
Write-Host "4. Teste sua aplicação após o deploy" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Boa sorte com seu deploy no Hostinger!" -ForegroundColor Green