# Instruções para Webhook do Stripe

## 🎯 Configuração Implementada

### ✅ Backend (Render)
- **Endpoint**: `https://bwhale.site/webhook/stripe`
- **Variável de ambiente**: `STRIPE_WEBHOOK_SECRET` já configurada
- **Eventos suportados**:
  - `checkout.session.completed` - Pagamento confirmado
  - `customer.subscription.created` - Assinatura criada
  - `customer.subscription.updated` - Assinatura atualizada
  - `customer.subscription.deleted` - Assinatura cancelada

### ✅ Frontend
- **Página de aguardo**: `/payment-waiting`
- **Verificação automática**: A cada 10 segundos por 5 minutos
- **Redirecionamento**: Para dashboard após confirmação

## 🔧 Configuração do Stripe (Já Feita)

Baseado nas imagens fornecidas, você já tem:
- **Webhook URL**: `https://bwhale.site/webhook/stripe`
- **Evento**: `checkout.session.completed` ✅
- **Segredo**: `whsec_IBYAR5rKEmay1AvbYgzBXOlmTaqEYLNb` ✅

## 🚀 Fluxo Completo

1. **Cliente clica em "Assinar"**
   - Sistema valida se email foi preenchido
   - Salva email no localStorage
   - Abre página do Stripe
   - Redireciona para `/payment-waiting`

2. **Página de aguardo**
   - Verifica status do pagamento a cada 10 segundos
   - Mostra progresso visual
   - Timeout de 5 minutos

3. **Stripe processa pagamento**
   - Envia webhook para `https://bwhale.site/webhook/stripe`
   - Backend verifica assinatura
   - Ativa usuário no banco de dados

4. **Confirmação automática**
   - Usuário é redirecionado para dashboard
   - Login automático

## 🧪 Como Testar

### 1. Teste do Webhook
```bash
# Verificar se webhook está funcionando
curl https://bwhale.site/webhook/stripe/test
```

### 2. Teste do Fluxo Completo
1. Acessar `https://bwhale.site/login`
2. Preencher email
3. Clicar em "🧪 Teste Webhook"
4. Completar pagamento no Stripe
5. Aguardar confirmação automática

### 3. Verificar Logs
- Logs do webhook estão disponíveis no Render
- Procurar por: `=== WEBHOOK STRIPE RECEBIDO ===`

## ⚠️ Troubleshooting

### Se o webhook não funcionar:
1. **Verificar URL**: Certificar que `https://bwhale.site/webhook/stripe` está acessível
2. **Verificar segredo**: Confirmar `STRIPE_WEBHOOK_SECRET` no Render
3. **Verificar eventos**: Confirmar que `checkout.session.completed` está habilitado
4. **Verificar logs**: Acessar logs do Render para debug

### Se o usuário não for ativado:
1. Verificar se email está correto
2. Verificar se webhook foi processado
3. Verificar banco de dados

## 📋 Checklist Final

- [ ] Webhook configurado no Stripe
- [ ] Backend deployed no Render
- [ ] Frontend com botão de teste
- [ ] Teste com pagamento real
- [ ] Verificação de logs
- [ ] Confirmação de ativação do usuário

## 🎉 Próximos Passos

Após confirmar que o webhook está funcionando com o link de teste, você pode:
1. Remover o botão "🧪 Teste Webhook"
2. Usar apenas os botões de produção
3. Monitorar logs para garantir funcionamento
4. Configurar alertas para falhas no webhook 