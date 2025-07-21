# 🚀 **GUIA DEFINITIVO - DEPLOY BACKEND NO RENDER**

## 📋 **PRÉ-REQUISITOS**
- ✅ Conta no GitHub
- ✅ Conta no Render.com 
- ✅ Projeto commitado no GitHub

## 🔧 **PREPARAÇÃO DOS ARQUIVOS**

### **1. Verificar arquivos essenciais:**
```
backend/
├── app_corrigido.py      # ✅ Arquivo principal da aplicação
├── requirements.txt      # ✅ Dependências Python
├── Procfile             # ✅ Comando de execução
├── render.yaml          # ✅ Configuração do Render
└── database.py          # ✅ Configuração do banco
```

### **2. Configuração do Procfile:**
```
web: gunicorn --bind 0.0.0.0:$PORT app_corrigido:application
```

### **3. Variáveis de ambiente necessárias:**
```
FLASK_SECRET_KEY=uma-chave-secreta-bem-dificil-de-adivinhar-987654
AES_ENCRYPTION_KEY=chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789
FLASK_ENV=production
STRIPE_WEBHOOK_SECRET=whsec_1BYR0SrkEmay1AvbYgzBX01mTaqEYLNb
RENDER=true
```

## 🌐 **PROCESSO DE DEPLOY NO RENDER**

### **PASSO 1: Preparar Repositório**
1. Faça commit de todos os arquivos:
```bash
git add .
git commit -m "Preparação para deploy no Render"
git push origin main
```

### **PASSO 2: Criar Serviço no Render**
1. Acesse [render.com](https://render.com)
2. Faça login com GitHub
3. Clique em **"New Web Service"**
4. Conecte seu repositório GitHub
5. Configure:
   - **Name:** `bigwhale-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && gunicorn --bind 0.0.0.0:$PORT app_corrigido:application`
   - **Root Directory:** `backend`

### **PASSO 3: Configurar Variáveis de Ambiente**
No painel do Render, adicione as variáveis:
```
FLASK_SECRET_KEY = uma-chave-secreta-bem-dificil-de-adivinhar-987654
AES_ENCRYPTION_KEY = chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789  
FLASK_ENV = production
STRIPE_WEBHOOK_SECRET = whsec_1BYR0SrkEmay1AvbYgzBX01mTaqEYLNb
RENDER = true
```

### **PASSO 4: Deploy e Verificação**
1. Clique em **"Create Web Service"**
2. Aguarde o build completar (5-10 minutos)
3. Teste o endpoint: `https://SEU-APP.onrender.com/api/health`

## ✅ **VERIFICAÇÃO DE FUNCIONAMENTO**

### **URLs para testar:**
- Health Check: `https://bigwhale-backend.onrender.com/api/health`
- Login: `https://bigwhale-backend.onrender.com/api/auth/login`

### **Logs importantes:**
```
✅ Nautilus startup
✅ Tabelas do banco de dados garantidas na inicialização
✅ Admin credentials ensured
✅ Invite codes initialized
```

## 🔧 **RESOLUÇÃO DE PROBLEMAS**

### **Se der erro de banco de dados:**
- O SQLite será criado automaticamente em `/tmp/site.db` no Render
- Dados serão recriados a cada deploy (normal para plano gratuito)

### **Se der erro de CORS:**
- Domínios permitidos já configurados para `bwhale.site`
- Adicione novos domínios no arquivo `app_corrigido.py`

### **Se der timeout:**
- Render gratuito "dorme" após inatividade
- Primeira requisição pode demorar 30+ segundos

## 📝 **URL FINAL**
Seu backend estará disponível em:
```
https://bigwhale-backend.onrender.com
```

Esta URL deve ser usada no frontend para conectar com a API. 