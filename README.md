# Deploy no Render

Este diretório contém arquivos otimizados para deploy no Render.

## Arquivos Incluídos

1. **`app_corrigido.py`** - Versão otimizada da aplicação Flask
2. **`build.sh`** - Script de build que instala psycopg2 antes de outras dependências
3. **`render.yaml`** - Configuração do Render
4. **`requirements.txt`** - Dependências otimizadas

## Como Fazer o Deploy

1. No painel do Render, crie um novo Web Service
2. Conecte ao repositório GitHub
3. Configure as seguintes opções:
   - **Nome**: bigwhale-backend
   - **Ambiente**: Python
   - **Build Command**: `chmod +x ./deployrender/build.sh && ./deployrender/build.sh`
   - **Start Command**: `gunicorn deployrender.app_corrigido:application`
   - **Versão do Python**: 3.9.16

4. Configure as variáveis de ambiente:
   ```
   DATABASE_URL = [URL do PostgreSQL]
   FLASK_SECRET_KEY = uma-chave-secreta-bem-dificil-de-adivinhar-987654
   CORS_ORIGINS = https://bwhale.site,https://bigwhale-backend.onrender.com
   ENVIRONMENT = production
   RENDER = true
   ```

5. Clique em "Create Web Service"

## Verificação

Após o deploy, acesse:

1. **Rota Raiz**: `https://bigwhale-backend.onrender.com/`
2. **Health Check**: `https://bigwhale-backend.onrender.com/api/health`
3. **Login**: Teste o login com as credenciais:
   - Email: `financeiro@lexxusadm.com.br`
   - Senha: `FinanceiroDemo2025@`