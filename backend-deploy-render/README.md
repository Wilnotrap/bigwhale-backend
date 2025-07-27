# BigWhale Backend - Deploy no Render

## 🚀 Instruções para Atualizar o Backend no Render

### Problema Identificado
O backend atual no Render (`https://bigwhale-backend.onrender.com`) está retornando erro 500 devido a:
- Procfile incorreto (tentando importar `app_corrigido:application` em vez de `app:application`)
- Possíveis problemas de dependências
- Configuração de banco de dados PostgreSQL incorreta

### Solução
Este diretório contém uma versão **corrigida e otimizada** do backend:
- ✅ Procfile correto
- ✅ Dependências atualizadas com psycopg2
- ✅ **PostgreSQL em produção** (Render) com fallback para SQLite (desenvolvimento)
- ✅ Endpoints essenciais funcionando
- ✅ CORS configurado para `bwhale.site`
- ✅ **Preservação de dados** - usa o PostgreSQL existente no Render

## 📋 Passos para Atualizar

### 1. Fazer Backup (Opcional)
```bash
# Clone o repositório atual para backup
git clone https://github.com/Wilnotrap/bigwhale-backend.git backup-bigwhale
```

### 2. Substituir Arquivos no Repositório GitHub

1. **Acesse seu repositório**: https://github.com/Wilnotrap/bigwhale-backend

2. **Substitua os arquivos principais**:
   - `app.py` (substitui o `app_corrigido.py`)
   - `Procfile`
   - `requirements.txt`

3. **Método via GitHub Web**:
   - Clique em cada arquivo no GitHub
   - Clique no ícone de lápis (Edit)
   - Copie o conteúdo dos arquivos desta pasta
   - Cole no GitHub
   - Commit as mudanças

4. **Método via Git Local**:
   ```bash
   git clone https://github.com/Wilnotrap/bigwhale-backend.git
   cd bigwhale-backend
   
   # Copie os arquivos desta pasta para o repositório
   # Depois:
   git add .
   git commit -m "Fix: Corrigir backend para deploy no Render"
   git push origin main
   ```

### 3. Verificar Deploy Automático

1. **Acesse o Render Dashboard**: https://dashboard.render.com
2. **Encontre seu serviço**: `bigwhale-backend`
3. **Aguarde o deploy automático** (será acionado pelo push no GitHub)
4. **Monitore os logs** para verificar se não há erros

### 4. Testar o Backend

Após o deploy, teste os endpoints:

```bash
# Health check
curl https://bigwhale-backend.onrender.com/api/health

# Deve retornar algo como:
{
  "status": "healthy",
  "message": "BigWhale Backend funcionando no Render",
  "database": "connected",
  "version": "1.0.0"
}
```

## 🔧 Configurações no Render

### Variáveis de Ambiente Necessárias
No painel do Render, certifique-se de que existem:
- ✅ `DATABASE_URL`: URL do PostgreSQL (configurada automaticamente pelo Render)
- `FLASK_SECRET_KEY`: Uma chave secreta personalizada (opcional)
- `AES_ENCRYPTION_KEY`: Chave para criptografia (opcional)

### PostgreSQL Database
- ✅ **Hostname**: Configurado automaticamente
- ✅ **Port**: 5432 (padrão PostgreSQL)
- ✅ **Database**: Nome do banco configurado
- ✅ **Username/Password**: Configurados automaticamente
- ✅ **Internal/External URLs**: Geradas automaticamente pelo Render

### Configurações Automáticas
- ✅ **Build Command**: Automático (pip install -r requirements.txt)
- ✅ **Start Command**: Definido no Procfile
- ✅ **Python Version**: Detectado automaticamente
- ✅ **Database Connection**: Automática via DATABASE_URL

## 📱 Endpoints Disponíveis

- `GET /` - Informações da API
- `GET /api/health` - Health check
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/register` - Registro de usuário
- `POST /api/credentials/save` - Salvar credenciais API
- `POST /api/credentials/validate` - Validar credenciais

## 👤 Usuário Admin Padrão

- **Email**: admin@bigwhale.com
- **Senha**: Raikamaster1@

## 🔄 Próximos Passos

1. **Atualizar Frontend**: Certifique-se de que o frontend está apontando para:
   ```javascript
   const API_URL = 'https://bigwhale-backend.onrender.com';
   ```

2. **Testar Integração**: Teste login, registro e outras funcionalidades

3. **Monitorar Logs**: Acompanhe os logs no Render para identificar possíveis problemas

## ⚠️ Notas Importantes

- **PostgreSQL**: Este backend usa PostgreSQL em produção (Render) e SQLite em desenvolvimento
- **Dados**: Os dados existentes no PostgreSQL do Render serão **preservados**
- **Migração**: O backend detecta automaticamente o ambiente e usa o banco apropriado
- **Compatibilidade**: Funciona tanto localmente (SQLite) quanto no Render (PostgreSQL)
- **Backup**: Recomendado fazer backup dos dados antes de grandes atualizações

## 🆘 Solução de Problemas

### Se o deploy falhar:
1. Verifique os logs no Render Dashboard
2. Certifique-se de que todos os arquivos foram commitados
3. Verifique se o Procfile está correto
4. Confirme que o requirements.txt tem todas as dependências

### Se o health check falhar:
1. Aguarde alguns minutos (serviços gratuitos podem demorar para iniciar)
2. Verifique se o serviço está "Active" no Render
3. Consulte os logs para erros específicos

---

**✅ Com essas correções, seu backend deve funcionar perfeitamente no Render!**