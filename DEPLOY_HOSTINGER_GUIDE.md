# 🚀 Guia Completo de Deploy no Hostinger - Nautilus Automação

## 📋 Pré-requisitos
### 1. Conta Hostinger
- Hospedagem compartilhada, VPS ou Cloud
- Acesso ao hPanel/cPanel
- Domínio configurado

### 2. Arquivos Preparados
- Arquivo ZIP de deploy gerado (`nautilus-deploy-YYYYMMDD-HHMMSS.zip`)
- Instruções de deploy (`INSTRUCOES_DEPLOY.txt`)

---

## 🌐 Passo 1: Acessar o Painel de Controle

### 1.1 Login no Hostinger
1. Acesse [hostinger.com.br](https://hostinger.com.br)
2. Faça login com suas credenciais
3. Vá para **hPanel** (painel principal)

### 1.2 Acessar o Gerenciador de Arquivos
1. No hPanel, procure por **"Gerenciador de Arquivos"** na seção **Arquivos**
2. Ou se tiver cPanel, acesse **cPanel → File Manager**
3. Navegue até a pasta **`public_html/`**

---

## 📦 Passo 2: Preparar o Ambiente

### 2.1 Backup (IMPORTANTE!)
1. Selecione todos os arquivos em `public_html/`
2. Clique com botão direito → **Compress** (Compactar)
3. Salve como `backup-YYYYMMDD.zip`
4. Baixe o backup para seu computador

### 2.2 Limpar public_html
1. Selecione todos os arquivos (exceto `.well-known` se existir)
2. Delete os arquivos antigos
3. Mantenha a pasta vazia e limpa

---

## 📤 Passo 3: Upload dos Arquivos

### 3.1 Upload do Arquivo ZIP
1. No Gerenciador de Arquivos, clique em **"Upload"**
2. Selecione o arquivo `nautilus-deploy-YYYYMMDD-HHMMSS.zip`
3. Aguarde o upload completar (limite: 256MB no hPanel)

### 3.2 Extrair Arquivos
1. Clique com botão direito no arquivo ZIP
2. Selecione **"Extract"** (Extrair)
3. Escolha extrair para **`public_html/`**
4. Confirme a extração

### 3.3 Verificar Estrutura
Após a extração, você deve ter:
```
public_html/
├── index.html (frontend React)
├── static/ (CSS/JS do React)
├── api/
│   ├── app.py
│   ├── app.wsgi
│   ├── requirements.txt
│   ├── .env.production
│   └── [outros arquivos Python]
├── .htaccess
└── [outros arquivos do frontend]
```

---

## ⚙️ Passo 4: Configurar Permissões

### 4.1 Permissões da API
1. Navegue até `public_html/api/`
2. Selecione a pasta `api`
3. Clique com botão direito → **"Permissions"**
4. Defina como **755** (rwxr-xr-x)
5. Marque **"Recurse into subdirectories"**
6. Aplique as permissões

### 4.2 Verificar .htaccess
Certifique-se de que os arquivos `.htaccess` estão presentes:
- `public_html/.htaccess` (frontend)
- `public_html/api/.htaccess` (backend)

---

## 🐍 Passo 5: Configurar Python (se disponível)

### 5.1 Via Terminal SSH (VPS/Cloud)
Se você tem acesso SSH:
```bash
cd public_html/api
pip install -r requirements.txt
```

### 5.2 Via Python App Manager (Hostinger)
1. No hPanel, procure por **"Python"** ou **"Python App"**
2. Crie uma nova aplicação Python
3. Defina o diretório como `public_html/api`
4. Instale as dependências do `requirements.txt`

### 5.3 Hospedagem Compartilhada
Se não tiver acesso a Python personalizado:
- Verifique se o Hostinger suporta Python na sua hospedagem
- Entre em contato com o suporte para ativar Python
- Considere upgrade para VPS se necessário

---

## 🔒 Passo 6: Configurar SSL

### 6.1 SSL Gratuito Hostinger
1. No hPanel, vá para **"SSL"**
2. Ative o **SSL gratuito** para seu domínio
3. Aguarde a ativação (pode levar até 24h)

### 6.2 Forçar HTTPS
O arquivo `.htaccess` já está configurado para redirecionar HTTP para HTTPS.

---

## 🧪 Passo 7: Testes e Verificações

### 7.1 Checklist de Verificação
- [ ] Frontend carrega em `https://seudominio.com`
- [ ] Não há erros 404 para arquivos CSS/JS
- [ ] API responde em `https://seudominio.com/api/health`
- [ ] Login funciona corretamente
- [ ] SSL está ativo e funcionando
- [ ] Redirecionamento HTTP → HTTPS funciona

### 7.2 Endpoints de Teste
```bash
# Teste do frontend
curl https://seudominio.com

# Teste da API
curl https://seudominio.com/api/health

# Teste de login
curl -X POST https://seudominio.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test", "password":"test"}'
```

---

## 🚨 Passo 8: Monitoramento e Logs

### 8.1 Logs do Hostinger
- **Error Logs:** hPanel → Logs → Error Logs
- **Access Logs:** hPanel → Logs → Access Logs
- **Python Logs:** Se usando Python App Manager

### 8.2 Monitoramento
- Configure alertas de uptime
- Monitore uso de recursos
- Verifique logs regularmente

---

## 🔧 Troubleshooting

### Problemas Comuns

**Erro 500 - Internal Server Error**
- Verifique Error Logs no hPanel
- Confirme permissões da pasta `api/` (755)
- Verifique se Python está disponível

**API não responde**
- Confirme se `app.wsgi` está configurado
- Verifique se dependências Python estão instaladas
- Teste se o arquivo `app.py` está acessível

**CORS Error**
- Verifique configuração de domínio no `.env.production`
- Confirme se `.htaccess` da API está correto

**Frontend não carrega**
- Verifique se `index.html` está em `public_html/`
- Confirme se arquivos `static/` estão presentes
- Teste se `.htaccess` principal está funcionando

**SSL não funciona**
- Aguarde até 24h para ativação
- Verifique se domínio está apontando corretamente
- Entre em contato com suporte Hostinger

---

## 📞 Suporte

### Hostinger
- **Chat 24/7:** Disponível no hPanel
- **Base de Conhecimento:** support.hostinger.com
- **Comunidade:** community.hostinger.com

### Documentação
- **Guia Completo:** `DEPLOY_HOSTINGER_GUIDE.md` (este arquivo)
- **Instruções Específicas:** `INSTRUCOES_DEPLOY.txt`
- **Checklist:** `CHECKLIST_PRE_DEPLOY.txt`

---

## ✅ Checklist Final

- [ ] Backup realizado
- [ ] Arquivo ZIP enviado e extraído
- [ ] Permissões configuradas (755 para api/)
- [ ] Python configurado (se disponível)
- [ ] SSL ativado
- [ ] Frontend funcionando
- [ ] API respondendo
- [ ] Login testado
- [ ] Logs verificados
- [ ] Monitoramento configurado

---

## 🎉 Parabéns!

Seu sistema **Nautilus Automação** está agora rodando no Hostinger!

**URLs importantes:**
- Site: `https://seudominio.com`
- API: `https://seudominio.com/api`
- Health Check: `https://seudominio.com/api/health`

**Próximos passos:**
1. Configure monitoramento de uptime
2. Implemente backups automáticos
3. Configure alertas de erro
4. Documente credenciais de acesso

---

*Guia criado para Nautilus Automação - Deploy no Hostinger*
*Última atualização: Janeiro 2025*