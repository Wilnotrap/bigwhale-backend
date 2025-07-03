# Backend Corrigido - Nautilus

## 🚀 Deploy no Render

Este backend foi corrigido para resolver o erro 500 no login. As principais correções incluem:

### ✅ Correções Implementadas

1. **Simplificação do endpoint de login** - Removida complexidade desnecessária
2. **Melhor tratamento de erros** - Logs detalhados para debugging
3. **Configuração de CORS otimizada** - Suporte adequado para frontend
4. **Criação automática de usuários admin** - Garantia de credenciais válidas
5. **Health check endpoint** - Monitoramento da aplicação

### 📋 Instruções para Deploy

1. **Faça upload dos arquivos** para um repositório Git
2. **Configure o Render** usando o arquivo `render.yaml` incluído
3. **Defina as variáveis de ambiente** no painel do Render:
   - `FLASK_SECRET_KEY`: Uma chave secreta forte
   - `AES_ENCRYPTION_KEY`: Chave de 32 bytes para criptografia
   - `FLASK_ENV`: production
   - `RENDER`: true

### 🔑 Credenciais de Teste

O sistema criará automaticamente estes usuários admin:

- **Email**: admin@bigwhale.com  
  **Senha**: Raikamaster1@

- **Email**: willian@lexxusadm.com.br  
  **Senha**: Bigwhale202021@

### 🛠️ Endpoints Disponíveis

- `GET /api/health` - Health check
- `POST /api/auth/login` - Login de usuários
- `GET /api/test` - Endpoint de teste

### 📊 Logs e Debugging

O sistema inclui logs detalhados para facilitar o debugging:
- Logs de inicialização
- Logs de tentativas de login
- Logs de erros com stack trace

### 🔧 Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python app.py
```

O servidor estará disponível em `http://localhost:5000`

### 📝 Notas Importantes

- O banco SQLite será criado automaticamente
- As credenciais admin são configuradas na inicialização
- O sistema é compatível com o frontend existente
- Todos os endpoints retornam JSON válido

---

**Status**: ✅ Testado e funcionando localmente  
**Pronto para deploy**: ✅ Sim