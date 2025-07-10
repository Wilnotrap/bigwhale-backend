# 🚀 Guia Completo de Deploy - BigWhale
## Frontend (Hostinger) + Backend (Render)

### 📋 **Problemas Identificados e Soluções**

#### 1. **Erro de CSP (Content Security Policy)**
- **Problema**: Google Fonts sendo bloqueadas
- **Solução**: `.htaccess` atualizado com CSP correto ✅

#### 2. **Erro de CORS**
- **Problema**: Frontend não consegue se comunicar com backend
- **Solução**: Configurações de CORS ajustadas ✅

#### 3. **Problemas de Login**
- **Problema**: Sessões não funcionando entre domínios
- **Solução**: Configurações de cookies e sessão ajustadas ✅

---

## 🛠️ **Passos para Deploy**

### **BACKEND (Render)**

#### 1. **Verificar Configuração do Render**
```yaml
# render.yaml
services:
  - type: web
    name: bigwhale-backend
    env: python
    runtime: python-3.10.12
    plan: free
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:application
    healthCheckPath: /api/health
    envVars:
      - key: FLASK_SECRET_KEY
        value: uma-chave-secreta-bem-dificil-de-adivinhar-987654
      - key: AES_ENCRYPTION_KEY  
        value: chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789
      - key: FLASK_ENV
        value: production
      - key: RENDER
        value: "1"
```

#### 2. **Testar Backend**
```bash
# Verificar se o backend está respondendo
curl https://bigwhale-backend.onrender.com/api/health

# Resposta esperada:
{
  "status": "healthy",
  "timestamp": "2024-XX-XX",
  "environment": "Render",
  "message": "Sistema BigWhale funcionando corretamente no Render"
}
```

---

### **FRONTEND (Hostinger)**

#### 1. **Preparar Build do Frontend**
```bash
cd frontend

# Instalar dependências
npm install

# Criar build de produção
npm run build:prod
```

#### 2. **Configurar Variáveis de Ambiente**
Criar arquivo `.env.production`:
```env
REACT_APP_API_URL=https://bigwhale-backend.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_DOMAIN=https://bwhale.site
GENERATE_SOURCEMAP=false
CI=false
```

#### 3. **Upload para Hostinger**
- Fazer upload dos arquivos da pasta `build/` para o diretório público da Hostinger
- Garantir que o arquivo `.htaccess` foi corrigido ✅

#### 4. **Verificar .htaccess**
O arquivo `.htaccess` deve conter:
```apache
# Content Security Policy - CORRIGIDO
Header set Content-Security-Policy "default-src 'self'; connect-src 'self' https://bigwhale-backend.onrender.com wss://bigwhale-backend.onrender.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com; script-src 'self' 'unsafe-inline' 'unsafe-eval';"

# CORS Headers para comunicação com backend
Header always set Access-Control-Allow-Origin "https://bigwhale-backend.onrender.com"
Header always set Access-Control-Allow-Credentials "true"
```

---

## 🔧 **Configurações Específicas**

### **1. Configurações de CORS (Backend)**
```python
# backend/app.py - Linha 72-82
CORS(app, 
     supports_credentials=True, 
     origins=[
         "https://bwhale.site",
         "http://bwhale.site",
         "http://localhost:3000"
     ],
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
```

### **2. Configurações de Sessão (Backend)**
```python
# Configurações de cookies para domínios cruzados
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=86400
)
```

### **3. Configurações de API (Frontend)**
```javascript
// frontend/src/config/api.js
const API_CONFIG = {
  baseURL: 'https://bigwhale-backend.onrender.com',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
};
```

---

## 🧪 **Testes Pós-Deploy**

### **1. Teste de Conectividade**
```bash
# Testar se o backend está respondendo
curl https://bigwhale-backend.onrender.com/api/health

# Testar se o frontend está carregando
curl https://bwhale.site
```

### **2. Teste de Login**
1. Acessar: `https://bwhale.site`
2. Fazer login com:
   - Email: `admin@bigwhale.com`
   - Senha: `Raikamaster1@`
3. Verificar se não há erros de CORS no console do navegador

### **3. Teste de Fontes**
1. Abrir DevTools do navegador
2. Verificar se as fontes do Google estão carregando
3. Não deve haver erros de CSP no console

---

## 📝 **Credenciais de Acesso**

### **Admin Principal**
- **Email**: `admin@bigwhale.com`
- **Senha**: `Raikamaster1@`

### **Admin Secundário**
- **Email**: `willian@lexxusadm.com.br`
- **Senha**: `Bigwhale202021@`

---

## 🔍 **Troubleshooting**

### **Problema: Fontes não carregam**
**Solução**: Verificar se o CSP no `.htaccess` inclui `https://fonts.googleapis.com`

### **Problema: Erro de CORS**
**Solução**: Verificar se o backend está configurado para aceitar `https://bwhale.site`

### **Problema: Login não funciona**
**Solução**: Verificar se `withCredentials: true` está configurado no frontend

### **Problema: Backend não responde**
**Solução**: Verificar se o Render está ativo e se o health check está funcionando

---

## 📞 **Monitoramento**

### **URLs Importantes**
- **Frontend**: https://bwhale.site
- **Backend**: https://bigwhale-backend.onrender.com
- **Health Check**: https://bigwhale-backend.onrender.com/api/health

### **Logs**
- **Render**: Acessar dashboard do Render para ver logs do backend
- **Hostinger**: Logs disponíveis no painel de controle

---

## ✅ **Checklist Final**

- [ ] Backend deployed no Render
- [ ] Health check funcionando
- [ ] Frontend built e uploaded para Hostinger
- [ ] .htaccess corrigido
- [ ] Teste de login funcionando
- [ ] Fontes carregando corretamente
- [ ] Sem erros de CORS no console
- [ ] Domínios corretos configurados

---

**🎉 Deploy concluído com sucesso!** 