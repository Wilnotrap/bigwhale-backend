from flask import Blueprint, request, jsonify
import json
import hmac
import hashlib
import os

stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

# Chave do webhook (deve ser configurada como variável de ambiente)
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_test_key')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

@stripe_webhook_bp.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    """
    Processa webhooks do Stripe para pagamentos e assinaturas
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verificar assinatura do webhook
        if not verify_stripe_signature(payload, sig_header):
            print(f"❌ Assinatura inválida. Header: {sig_header}")
            print(f"❌ Chave configurada: {STRIPE_WEBHOOK_SECRET[:20]}...")
            print(f"🔧 Ambiente: {ENVIRONMENT}")
            
            # Em desenvolvimento, apenas avisar mas continuar
            if ENVIRONMENT == 'development':
                print("⚠️ DESENVOLVIMENTO: Continuando sem validação de assinatura")
            else:
                return jsonify({'error': 'Invalid signature'}), 400

        # Parse do evento
        event = json.loads(payload)
        event_type = event.get('type', 'unknown')
        
        # Log do evento recebido
        print(f"🔔 Webhook recebido: {event_type}")
        
        # ==========================================
        # EVENTOS DE PAGAMENTO ÚNICO
        # ==========================================
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            
            # Extrair dados do cliente
            customer_email = session.get('customer_details', {}).get('email', '')
            session_id = session.get('id', '')
            subscription_id = session.get('subscription', '')
            
            print(f"✅ Checkout completado para: {customer_email}")
            print(f"📧 Session ID: {session_id}")
            print(f"🔄 Subscription ID: {subscription_id}")
            
            # Determinar tipo de pagamento
            if subscription_id:
                print("💰 ASSINATURA CRIADA")
                redirect_url = f'/register?payment_success=true&session_id={session_id}&subscription_id={subscription_id}'
            else:
                print("💳 PAGAMENTO ÚNICO")
                redirect_url = f'/register?payment_success=true&session_id={session_id}'
            
            return jsonify({
                'status': 'success',
                'message': 'Payment confirmed',
                'customer_email': customer_email,
                'session_id': session_id,
                'subscription_id': subscription_id,
                'redirect_url': redirect_url
            }), 200
            
        # ==========================================
        # EVENTOS DE ASSINATURA
        # ==========================================
        elif event_type == 'customer.subscription.created':
            subscription = event['data']['object']
            customer_id = subscription.get('customer', '')
            subscription_id = subscription.get('id', '')
            status = subscription.get('status', '')
            
            print(f"🎯 NOVA ASSINATURA CRIADA")
            print(f"   Customer ID: {customer_id}")
            print(f"   Subscription ID: {subscription_id}")
            print(f"   Status: {status}")
            
            return jsonify({
                'status': 'success',
                'message': 'Subscription created',
                'subscription_id': subscription_id,
                'customer_id': customer_id
            }), 200
            
        elif event_type == 'customer.subscription.updated':
            subscription = event['data']['object']
            subscription_id = subscription.get('id', '')
            status = subscription.get('status', '')
            
            print(f"🔄 ASSINATURA ATUALIZADA")
            print(f"   Subscription ID: {subscription_id}")
            print(f"   Novo Status: {status}")
            
            return jsonify({
                'status': 'success',
                'message': 'Subscription updated',
                'subscription_id': subscription_id,
                'status': status
            }), 200
            
        elif event_type == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            customer_email = invoice.get('customer_email', '')
            subscription_id = invoice.get('subscription', '')
            amount_paid = invoice.get('amount_paid', 0)
            invoice_id = invoice.get('id', '')
            
            print(f"💰 PAGAMENTO DE ASSINATURA SUCESSO")
            print(f"   Email: {customer_email}")
            print(f"   Subscription ID: {subscription_id}")
            print(f"   Valor pago: {amount_paid}")
            print(f"   Invoice ID: {invoice_id}")
            
            # Se é primeira fatura (subscription), redirecionar para registro
            if subscription_id and amount_paid > 0:
                return jsonify({
                    'status': 'success',
                    'message': 'Subscription payment confirmed',
                    'customer_email': customer_email,
                    'subscription_id': subscription_id,
                    'amount_paid': amount_paid,
                    'redirect_url': f'/register?payment_confirmed=true&subscription_id={subscription_id}'
                }), 200
            
            return jsonify({'status': 'success', 'message': 'Invoice payment processed'}), 200
            
        elif event_type == 'invoice.payment_failed':
            invoice = event['data']['object']
            customer_email = invoice.get('customer_email', '')
            subscription_id = invoice.get('subscription', '')
            
            print(f"❌ PAGAMENTO DE ASSINATURA FALHOU")
            print(f"   Email: {customer_email}")
            print(f"   Subscription ID: {subscription_id}")
            
            return jsonify({
                'status': 'payment_failed',
                'message': 'Subscription payment failed',
                'customer_email': customer_email,
                'subscription_id': subscription_id
            }), 200
            
        # ==========================================
        # OUTROS EVENTOS
        # ==========================================
        elif event_type == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment_id = payment_intent.get('id', '')
            amount = payment_intent.get('amount', 0)
            
            print(f"✅ Payment Intent confirmado: {payment_id}")
            print(f"💵 Valor: {amount}")
            
            return jsonify({
                'status': 'success',
                'message': 'Payment intent succeeded',
                'payment_id': payment_id,
                'amount': amount
            }), 200
            
        else:
            print(f"📝 Evento não processado: {event_type}")
            return jsonify({
                'status': 'ignored',
                'message': f'Event type {event_type} not processed',
                'event_type': event_type
            }), 200

    except json.JSONDecodeError:
        print(f"❌ Erro JSON: Payload inválido")
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Webhook processing failed'}), 500

def verify_stripe_signature(payload, signature_header):
    """
    Verifica a assinatura do webhook do Stripe
    """
    # Em desenvolvimento, aceitar qualquer assinatura
    if ENVIRONMENT == 'development' and STRIPE_WEBHOOK_SECRET == 'whsec_test_key':
        print("🔧 DESENVOLVIMENTO: Assinatura aceita automaticamente")
        return True
    
    if not signature_header:
        print("❌ Cabeçalho de assinatura ausente")
        return False
    
    try:
        elements = signature_header.split(',')
        signature_dict = {}
        
        for element in elements:
            if '=' in element:
                key, value = element.split('=', 1)
                signature_dict[key.strip()] = value.strip()
        
        timestamp = signature_dict.get('t')
        signature = signature_dict.get('v1')
        
        if not timestamp or not signature:
            print(f"❌ Timestamp ou assinatura ausentes: t={timestamp}, v1={signature}")
            return False
        
        # Criar string assinada
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        
        # Calcular hash esperado
        expected_signature = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Comparar assinaturas
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if is_valid:
            print("✅ Assinatura verificada com sucesso")
        else:
            print("❌ Assinatura inválida")
            
        return is_valid
        
    except Exception as e:
        print(f"❌ Erro na verificação da assinatura: {str(e)}")
        return False

@stripe_webhook_bp.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """
    Endpoint de teste para verificar se o webhook está funcionando
    """
    return jsonify({
        'status': 'ok',
        'message': 'Webhook endpoint is working',
        'method': request.method
    }), 200

@stripe_webhook_bp.route('/webhook/success', methods=['GET'])
def webhook_success():
    """
    Página de sucesso após pagamento
    """
    return jsonify({
        'status': 'success',
        'message': 'Pagamento processado com sucesso!',
        'next_steps': [
            'Verifique seu email para confirmação',
            'Acesse sua conta para configurar suas credenciais',
            'Entre em contato conosco se tiver dúvidas'
        ]
    })

@stripe_webhook_bp.route('/webhook/status', methods=['GET'])
def check_webhook_status():
    """
    Verifica status geral do webhook
    """
    return jsonify({
        'status': 'active',
        'message': 'Webhook funcionando corretamente',
        'endpoints': [
            '/api/webhook/stripe - Recebe webhooks do Stripe',
            '/api/webhook/test - Endpoint de teste',
            '/api/webhook/success - Página de sucesso',
            '/api/webhook/status - Status do webhook'
        ]
    }) 