# 🚀 Guia Completo de Deploy no GoDaddy - Nautilus Automação

## 📋 Pré-requisitos

### 1. Conta GoDaddy
- Hospedagem compartilhada ou VPS
- Acesso ao cPanel
- Domínio configurado

### 2. Preparação Local
- Node.js instalado
- Python 3.x instalado
- Projeto funcionando localmente

## 🏗️ Estrutura de Deploy

```
Domínio Principal (exemplo.com)
├── Frontend React (build estático)
├── Backend Flask (/api)
└── Banco de dados SQLite/MySQL
```

## 📦 Passo 1: Preparar o Frontend

### 1.1 Configurar Variáveis de Produção

**Criar `.env.production`:**
```bash
# Frontend - .env.production
REACT_APP_API_URL=https://seudominio.com/api
REACT_APP_ENVIRONMENT=production
REACT_APP_ENABLE_SECURITY_LOGS=false
GENERATE_SOURCEMAP=false
```

### 1.2 Atualizar Configurações de Segurança

**Arquivo `src/config/security.config.js`:**
```javascript
export const SECURITY_CONFIG = {
  // ... configurações existentes ...
  CSP: {
    DIRECTIVES: {
      'default-src': ["'self'"],
      'script-src': ["'self'"],
      'style-src': ["'self'", "'unsafe-inline'"],
      'img-src': ["'self'", 'data:', 'https:'],
      'connect-src': [
        "'self'", 
        'https://seudominio.com',
        // Manter antivírus
        '*.kaspersky-labs.com',
        '*.avast.com',
        '*.avg.com'
      ],
      'font-src': ["'self'"],
      'object-src': ["'none'"],
      'media-src': ["'self'"],
      'frame-src': ["'none'"]
    }
  }
};
```

### 1.3 Build de Produção

```bash
cd frontend
npm run build:secure
```

## 🐍 Passo 2: Preparar o Backend

### 2.1 Criar requirements.txt Otimizado

```txt
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Session==0.5.0
requests==2.31.0
APScheduler==3.10.4
sqlite3
gunicorn==21.2.0
```

### 2.2 Configurar Variáveis de Ambiente

**Criar `.env.production`:**
```bash
# Backend - .env.production
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=sua_chave_super_secreta_aqui
DATABASE_URL=sqlite:///instance/site.db
API_BASE_URL=https://seudominio.com/api
CORS_ORIGINS=https://seudominio.com
```

### 2.3 Criar app.wsgi para GoDaddy

**Arquivo `app.wsgi`:**
```python
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
```

### 2.4 Atualizar app.py para Produção

```python
# Adicionar no início do app.py
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
else:
    load_dotenv()

# Configurações de produção
app.config['DEBUG'] = False
app.config['TESTING'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# CORS para produção
CORS(app, origins=os.environ.get('CORS_ORIGINS', 'https://seudominio.com'))
```

## 🌐 Passo 3: Upload para GoDaddy

### 3.1 Estrutura de Diretórios no cPanel

```
public_html/
├── index.html (do build React)
├── static/ (arquivos CSS/JS do React)
├── api/
│   ├── app.py
│   ├── app.wsgi
│   ├── requirements.txt
│   ├── .env.production
│   ├── backend/ (todos os arquivos Python)
│   └── instance/
│       └── site.db
└── .htaccess
```

### 3.2 Upload do Frontend

1. **Via cPanel File Manager:**
   - Acesse cPanel → File Manager
   - Navegue até `public_html/`
   - Upload todos os arquivos da pasta `build/`
   - Extrair se necessário

2. **Via FTP:**
   ```bash
   # Usando FileZilla ou WinSCP
   # Upload: build/* → public_html/
   ```

### 3.3 Upload do Backend

1. **Criar pasta `api/` em `public_html/`**
2. **Upload todos os arquivos Python:**
   - `app.py`
   - `app.wsgi`
   - `requirements.txt`
   - `.env.production`
   - Pasta `backend/` completa
   - Pasta `instance/` com banco

## ⚙️ Passo 4: Configurar .htaccess

### 4.1 .htaccess Principal (public_html/)

```apache
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
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://seudominio.com; font-src 'self'; object-src 'none'; media-src 'self'; frame-src 'none'"

# Roteamento para API
RewriteRule ^api/(.*)$ /api/app.wsgi/$1 [QSA,L]

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
```

### 4.2 .htaccess da API (public_html/api/)

```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ app.wsgi/$1 [QSA,L]

# Headers CORS
Header always set Access-Control-Allow-Origin "https://seudominio.com"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization, X-CSRF-Token"
```

## 🗄️ Passo 5: Configurar Banco de Dados

### 5.1 SQLite (Recomendado para início)

```python
# No app.py
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
```

### 5.2 MySQL (Para maior escala)

1. **Criar banco no cPanel:**
   - cPanel → MySQL Databases
   - Criar banco: `nautilus_db`
   - Criar usuário e dar permissões

2. **Configurar conexão:**
```python
# .env.production
DATABASE_URL=mysql://usuario:senha@localhost/nautilus_db
```

## 🔧 Passo 6: Instalar Dependências Python

### 6.1 Via cPanel Terminal (se disponível)

```bash
cd public_html/api
python3 -m pip install --user -r requirements.txt
```

### 6.2 Via SSH (se disponível)

```bash
ssh usuario@seudominio.com
cd public_html/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🧪 Passo 7: Testes e Verificações

### 7.1 Checklist de Verificação

- [ ] Frontend carrega em `https://seudominio.com`
- [ ] API responde em `https://seudominio.com/api/health`
- [ ] Login funciona
- [ ] HTTPS ativo
- [ ] Headers de segurança presentes
- [ ] Console limpo em produção
- [ ] Performance adequada

### 7.2 Endpoints de Teste

```bash
# Testar API
curl https://seudominio.com/api/health

# Testar headers de segurança
curl -I https://seudominio.com
```

## 🚨 Passo 8: Monitoramento e Logs

### 8.1 Logs do GoDaddy

- **Error Logs:** cPanel → Error Logs
- **Access Logs:** cPanel → Raw Access Logs

### 8.2 Monitoramento de Aplicação

```python
# Adicionar ao app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/nautilus.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Nautilus startup')
```

## 🔒 Passo 9: Segurança Adicional

### 9.1 SSL/TLS

- **GoDaddy SSL:** Ativar no cPanel
- **Let's Encrypt:** Se disponível
- **Forçar HTTPS:** Via .htaccess

### 9.2 Backup Automático

```bash
# Script de backup (executar via cron)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz public_html/
```

## 🚀 Passo 10: Otimizações

### 10.1 Performance

- **Compressão Gzip:** Ativada via .htaccess
- **Cache:** Headers de cache configurados
- **CDN:** Considerar Cloudflare

### 10.2 SEO

```html
<!-- Adicionar ao public/index.html -->
<meta name="description" content="Nautilus Automação - Plataforma de Trading">
<meta name="keywords" content="trading, automação, bitcoin, crypto">
<meta property="og:title" content="Nautilus Automação">
<meta property="og:description" content="Plataforma de Trading Automatizado">
```

## 📞 Suporte e Troubleshooting

### Problemas Comuns:

1. **500 Internal Server Error:**
   - Verificar logs de erro
   - Checar permissões de arquivo
   - Validar .htaccess

2. **API não responde:**
   - Verificar app.wsgi
   - Checar dependências Python
   - Validar variáveis de ambiente

3. **CORS Error:**
   - Verificar headers CORS
   - Validar domínio na configuração

### Contatos de Suporte:
- **GoDaddy:** Suporte técnico 24/7
- **Documentação:** help.godaddy.com

---

## ✅ Checklist Final

- [ ] Build de produção criado
- [ ] Variáveis de ambiente configuradas
- [ ] Arquivos enviados via FTP/cPanel
- [ ] .htaccess configurado
- [ ] Dependências Python instaladas
- [ ] Banco de dados configurado
- [ ] SSL ativado
- [ ] Testes realizados
- [ ] Monitoramento ativo
- [ ] Backup configurado

**🎉 Parabéns! Sua aplicação Nautilus está no ar!**