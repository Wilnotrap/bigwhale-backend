# 🐋 BigWhale Backend - Nautilus Trading Platform

## 🚀 Deploy Automático no Render

Este é o backend corrigido e otimizado do Nautilus, pronto para deploy no Render.

### ✅ Estrutura do Projeto

```
backend_github/
├── .gitignore          # Arquivos ignorados pelo Git
├── app.py              # Aplicação Flask principal
├── database.py         # Configuração do SQLAlchemy
├── requirements.txt    # Dependências Python
├── render.yaml         # Configuração do Render
├── models/
│   ├── __init__.py
│   └── user.py         # Modelo de usuário
└── README.md           # Este arquivo
```

### 🔧 Configuração no Render

1. **Conecte este repositório** ao Render
2. **Configure as variáveis de ambiente**:
   ```
   FLASK_SECRET_KEY=sua_chave_secreta_aqui
   AES_ENCRYPTION_KEY=sua_chave_32_bytes_aqui
   FLASK_ENV=production
   RENDER=true
   ```

### 🔑 Credenciais de Admin

O sistema criará automaticamente estes usuários:

- **Email**: `admin@bigwhale.com`  
  **Senha**: `Raikamaster1@`

- **Email**: `willian@lexxusadm.com.br`  
  **Senha**: `Bigwhale202021@`

### 📡 Endpoints da API

- `GET /api/health` - Health check do sistema
- `POST /api/auth/login` - Autenticação de usuários
- `GET /api/test` - Endpoint de teste

### 🛠️ Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python app.py
```

### 🔍 Logs e Debugging

O sistema inclui logs detalhados para facilitar o debugging:
- ✅ Logs de inicialização
- ✅ Logs de tentativas de login
- ✅ Logs de erros com stack trace
- ✅ Health check com contagem de usuários

### 🎯 Principais Correções

1. **Endpoint de login simplificado** - Removida complexidade desnecessária
2. **Criação automática de usuários admin** - Garantia de credenciais válidas
3. **Configuração de banco otimizada** - SQLite com criação automática
4. **CORS configurado** - Suporte adequado para frontend
5. **Health check robusto** - Monitoramento da aplicação

---

**Status**: ✅ Testado e funcionando  
**Deploy**: ✅ Pronto para produção  
**Compatibilidade**: ✅ Frontend existente