# Deploy do Frontend na Hostinger

## ⚠️ PROBLEMAS IDENTIFICADOS E SOLUÇÕES

### 🔧 Correções Aplicadas:

1. **❌ Erro CSP (Content Security Policy)**
   - **Problema**: Google Fonts bloqueado pela política de segurança
   - **✅ Solução**: Adicionada configuração CSP no `.htaccess` permitindo Google Fonts

2. **❌ Erro 500 no Backend**
   - **Problema**: Servidor backend retornando erro interno no login
   - **⚠️ Status**: Requer verificação no Render (backend pode estar "dormindo")

### 📋 Instruções para Deploy

#### 1. Preparação dos Arquivos
Todos os arquivos necessários para o deploy estão nesta pasta `frontend-deploy-hostinger`.

#### 2. Configuração do Backend
O frontend está configurado para se conectar ao backend hospedado no Render:
- **URL do Backend**: `https://bigwhale-backend.onrender.com`
- **Configuração**: Arquivo `.env.production` incluído
- **CSP**: Configurado para permitir conexões com o backend

#### 3. Arquivos Incluídos
- `index.html` - Página principal da aplicação
- `.htaccess` - **ATUALIZADO** com CSP e configurações de segurança
- `asset-manifest.json` - Manifesto dos assets
- `manifest.json` - Manifesto da PWA
- `static/` - Pasta com CSS, JS e imagens
- Favicons e logos

#### 4. Processo de Upload na Hostinger

1. **Acesse o painel da Hostinger**
2. **Vá para o File Manager**
3. **Navegue até a pasta `public_html`**
4. **Faça upload de TODOS os arquivos desta pasta**
5. **Mantenha a estrutura de pastas**

#### 5. Verificações Pós-Deploy

- ✅ Verifique se o site carrega corretamente
- ✅ Confirme se o Google Fonts carrega (sem erro CSP)
- ⚠️ Teste o login/cadastro (pode falhar se backend estiver "dormindo")
- ✅ Verifique se as rotas funcionam (SPA routing)
- ✅ Teste em diferentes dispositivos

#### 6. Configurações de Segurança (CSP)

O arquivo `.htaccess` agora inclui:
```
Content-Security-Policy: 
- default-src 'self'
- style-src 'self' 'unsafe-inline' https://fonts.googleapis.com
- font-src 'self' https://fonts.gstatic.com
- connect-src 'self' https://bigwhale-backend.onrender.com
- script-src 'self' 'unsafe-inline'
- img-src 'self' data:
```

#### 7. Solução para Backend "Dormindo"

Se o login falhar com erro 500:
1. **Acesse diretamente**: `https://bigwhale-backend.onrender.com`
2. **Aguarde 30-60 segundos** para o backend "acordar"
3. **Tente o login novamente**

#### 8. Domínio
O frontend está configurado para o domínio: `bwhale.site`

---

**✅ CORREÇÕES APLICADAS**: CSP configurado, headers de segurança otimizados
**⚠️ ATENÇÃO**: Backend no Render pode demorar para responder na primeira requisição