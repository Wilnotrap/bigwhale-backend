from flask import Blueprint, request, jsonify
import json
import hmac
import hashlib
import os

stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

# Chave do webhook (deve ser configurada como variável de ambiente)
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_test_key')

@stripe_webhook_bp.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    """
    Processa webhooks do Stripe para pagamentos
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verificar assinatura do webhook
        if not verify_stripe_signature(payload, sig_header):
            print(f"❌ Assinatura inválida. Header: {sig_header}")
            print(f"❌ Chave configurada: {STRIPE_WEBHOOK_SECRET[:20]}...")
            return jsonify({'error': 'Invalid signature'}), 400

        # Parse do evento
        event = json.loads(payload)
        
        # Log do evento recebido
        print(f"🔔 Webhook recebido: {event.get('type', 'unknown')}")
        
        # Processar diferentes tipos de eventos
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Extrair email do cliente se disponível
            customer_email = session.get('customer_details', {}).get('email', '')
            
            # Log do evento
            print(f"✅ Pagamento confirmado para: {customer_email}")
            print(f"📧 Session ID: {session['id']}")
            
            # Redirecionar para formulário de registro
            # O frontend vai detectar o sucesso e redirecionar
            return jsonify({
                'status': 'success',
                'message': 'Payment confirmed',
                'customer_email': customer_email,
                'redirect_url': '/register?payment_success=true'
            }), 200
            
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"✅ Payment Intent confirmado: {payment_intent['id']}")
            return jsonify({'status': 'success'}), 200
            
        else:
            print(f"📝 Evento não processado: {event['type']}")
            return jsonify({'status': 'ignored'}), 200

    except json.JSONDecodeError:
        print(f"❌ Erro JSON: Payload inválido")
        return jsonify({'error': 'Invalid JSON'}), 400
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

def verify_stripe_signature(payload, signature_header):
    """
    Verifica a assinatura do webhook do Stripe
    """
    if not signature_header:
        return False
    
    try:
        elements = signature_header.split(',')
        signature_dict = {}
        
        for element in elements:
            key, value = element.split('=')
            signature_dict[key] = value
        
        timestamp = signature_dict.get('t')
        signature = signature_dict.get('v1')
        
        if not timestamp or not signature:
            return False
        
        # Criar string assinada
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        
        # Calcular hash esperado
        expected_signature = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Em ambiente de desenvolvimento, aceitar qualquer assinatura
        if STRIPE_WEBHOOK_SECRET == 'whsec_test_key':
            return True
        
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception:
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