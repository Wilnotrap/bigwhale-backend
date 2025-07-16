# 🚀 Instruções de Deploy - BigWhale Backend

## 📁 Estrutura do Projeto

Esta pasta contém **APENAS** os arquivos necessários para deploy no Render:

```
Back Github/
├── backend/                 # Código Python da API
│   ├── api/                # Endpoints da API
│   ├── auth/               # Autenticação
│   ├── models/             # Modelos do banco
│   ├── services/           # Serviços (Nautilus, etc)
│   ├── utils/              # Utilitários
│   ├── app.py              # Aplicação principal
│   └── database.py         # Configuração do banco
├── requirements.txt        # Dependências Python
├── runtime.txt            # Versão do Python (3.11)
├── Procfile              # Comando de inicialização
├── render.yaml           # Configuração do Render
└── .gitignore           # Arquivos ignorados pelo Git
```

## 🔧 Passo a Passo para Deploy

### 1. Inicializar Git (Execute o arquivo .bat)
```bash
# Execute o arquivo inicializar_git.bat
# OU execute manualmente:
git init
git add .
git commit -m "Deploy inicial BigWhale Backend"
git branch -M main
```

### 2. Criar Repositório no GitHub
1. Acesse [GitHub](https://github.com)
2. Clique em "New repository"
3. Nome: `bigwhale-backend-deploy`
4. Deixe público ou privado (sua escolha)
5. **NÃO** adicione README, .gitignore ou license
6. Clique em "Create repository"

### 3. Conectar ao GitHub
```bash
git remote add origin https://github.com/SEU_USUARIO/bigwhale-backend-deploy.git
git push -u origin main
```

### 4. Configurar Deploy no Render

#### A. Criar Conta no Render
1. Acesse [render.com](https://render.com)
2. Faça login com GitHub

#### B. Criar Web Service
1. Clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório `bigwhale-backend-deploy`
4. Configure:

**Configurações Básicas:**
- **Name:** `bigwhale-backend`
- **Environment:** `Python 3`
- **Region:** `Oregon (US West)` ou mais próximo
- **Branch:** `main`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd backend && gunicorn app:application --bind 0.0.0.0:$PORT`

#### C. Configurar Variáveis de Ambiente
Na seção "Environment Variables", adicione:

| Key | Value | Tipo |
|-----|-------|------|
| `FLASK_SECRET_KEY` | *Gerar automaticamente* | Generate |
| `AES_ENCRYPTION_KEY` | *Gerar automaticamente* | Generate |
| `DATABASE_URL` | *Conectar PostgreSQL* | Database |

#### D. Criar Banco PostgreSQL
1. No dashboard do Render, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - **Name:** `bigwhale-db`
   - **Database Name:** `bigwhale`
   - **User:** `bigwhale_user`
   - **Region:** Mesmo do Web Service

4. Após criar, copie a "External Database URL"
5. Cole na variável `DATABASE_URL` do Web Service

### 5. Deploy Automático
- O Render fará deploy automaticamente
- Acompanhe os logs na interface
- URL final: `https://bigwhale-backend.onrender.com`

## 🔍 Verificar Deploy

### Endpoints para Testar:
- `GET /api/health` - Health check
- `GET /api/test` - Teste básico
- `POST /api/auth/login` - Login

### Teste no Browser:
```
https://SEU_APP.onrender.com/api/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "message": "Backend BigWhale funcionando no Render!",
  "database": "connected",
  "users_count": 0
}
```

## 🔄 Atualizações Futuras

Para atualizar o backend:
1. Faça as alterações no projeto principal
2. Execute novamente `organizar_deploy.py`
3. Commit e push:
```bash
cd "Back Github"
git add .
git commit -m "Atualização: descrição das mudanças"
git push origin main
```

## ⚠️ Problemas Comuns

### Build Falha
- Verifique se `requirements.txt` está correto
- Verifique se não há erros de sintaxe no código

### Database Connection Error
- Verifique se `DATABASE_URL` está configurada
- Verifique se o PostgreSQL está rodando

### CORS Errors
- Verifique se o domínio do frontend está nas configurações CORS
- Atual: `https://bwhale.site`

### 500 Internal Server Error
- Verifique os logs no dashboard do Render
- Verifique se todas as variáveis de ambiente estão configuradas

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no dashboard do Render
2. Teste os endpoints individualmente
3. Verifique se o banco de dados está conectado

## 🎯 Configurações Importantes

### CORS (já configurado)
```python
origins=[
    "https://bwhale.site",
    "http://bwhale.site",
    "http://localhost:3000"
]
```

### Banco de Dados
- **Produção:** PostgreSQL (Render)
- **Desenvolvimento:** SQLite (local)

### Integração Nautilus
- ✅ Mantida intacta
- ✅ Webhooks funcionando
- ✅ Cadastro com validação

---

**Data de criação:** 2025-07-15
**Versão:** 1.0
**Status:** Pronto para deploy