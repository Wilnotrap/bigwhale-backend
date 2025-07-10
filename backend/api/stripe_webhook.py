from flask import Blueprint, request, jsonify
import json
import hmac
import hashlib
import os
from datetime import datetime

stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

# Chave do webhook (deve ser configurada como variável de ambiente)
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_test_key')

# Log global para webhooks recebidos
webhook_logs = []

def log_webhook_event(event_type, message, data=None):
    """Log eventos do webhook para debug"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'message': message,
        'data': data
    }
    webhook_logs.append(log_entry)
    
    # Manter apenas os últimos 50 logs
    if len(webhook_logs) > 50:
        webhook_logs.pop(0)
    
    print(f"🔔 [{timestamp}] {event_type}: {message}")

@stripe_webhook_bp.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    """
    Processa webhooks do Stripe para pagamentos
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    log_webhook_event('RECEIVED', f'Webhook recebido com signature: {sig_header}')

    try:
        # Verificar assinatura do webhook
        if not verify_stripe_signature(payload, sig_header):
            log_webhook_event('ERROR', f'Assinatura inválida. Header: {sig_header}')
            log_webhook_event('ERROR', f'Chave configurada: {STRIPE_WEBHOOK_SECRET[:20]}...')
            return jsonify({'error': 'Invalid signature'}), 400

        # Parse do evento
        event = json.loads(payload)
        event_type = event.get('type', 'unknown')
        
        log_webhook_event('PARSED', f'Evento parseado: {event_type}')
        
        # Processar diferentes tipos de eventos
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            
            # Extrair dados do cliente
            customer_email = session.get('customer_details', {}).get('email', '')
            session_id = session.get('id', '')
            payment_status = session.get('payment_status', '')
            
            log_webhook_event('PAYMENT_SUCCESS', f'Pagamento confirmado para: {customer_email}')
            log_webhook_event('PAYMENT_SUCCESS', f'Session ID: {session_id}')
            log_webhook_event('PAYMENT_SUCCESS', f'Payment Status: {payment_status}')
            
            # Retornar sucesso com dados detalhados
            return jsonify({
                'status': 'success',
                'message': 'Payment confirmed',
                'customer_email': customer_email,
                'session_id': session_id,
                'payment_status': payment_status,
                'redirect_url': '/register?payment_success=true',
                'timestamp': datetime.now().isoformat()
            }), 200
            
        elif event_type == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment_id = payment_intent.get('id', '')
            
            log_webhook_event('PAYMENT_INTENT', f'Payment Intent confirmado: {payment_id}')
            
            return jsonify({
                'status': 'success',
                'message': 'Payment intent succeeded',
                'payment_id': payment_id,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        else:
            log_webhook_event('IGNORED', f'Evento não processado: {event_type}')
            return jsonify({
                'status': 'ignored',
                'message': f'Event type {event_type} not processed',
                'timestamp': datetime.now().isoformat()
            }), 200

    except json.JSONDecodeError as e:
        log_webhook_event('ERROR', f'Erro JSON: {str(e)}')
        return jsonify({'error': 'Invalid JSON', 'details': str(e)}), 400
    except Exception as e:
        log_webhook_event('ERROR', f'Erro geral: {str(e)}')
        return jsonify({'error': 'Webhook processing failed', 'details': str(e)}), 500

def verify_stripe_signature(payload, signature_header):
    """
    Verifica a assinatura do webhook do Stripe
    """
    if not signature_header:
        log_webhook_event('ERROR', 'Signature header ausente')
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
            log_webhook_event('ERROR', 'Timestamp ou signature ausentes')
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
            log_webhook_event('DEBUG', 'Modo de desenvolvimento - aceitando qualquer assinatura')
            return True
        
        # Comparar assinaturas
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if is_valid:
            log_webhook_event('SUCCESS', 'Assinatura válida')
        else:
            log_webhook_event('ERROR', f'Assinatura inválida. Esperado: {expected_signature[:20]}..., Recebido: {signature[:20]}...')
        
        return is_valid
        
    except Exception as e:
        log_webhook_event('ERROR', f'Erro ao verificar assinatura: {str(e)}')
        return False

@stripe_webhook_bp.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """
    Endpoint de teste para verificar se o webhook está funcionando
    """
    log_webhook_event('TEST', f'Endpoint de teste acessado via {request.method}')
    
    return jsonify({
        'status': 'ok',
        'message': 'Webhook endpoint is working',
        'method': request.method,
        'timestamp': datetime.now().isoformat(),
        'webhook_secret_configured': STRIPE_WEBHOOK_SECRET != 'whsec_test_key'
    }), 200

@stripe_webhook_bp.route('/webhook/logs', methods=['GET'])
def get_webhook_logs():
    """
    Retorna logs dos webhooks recebidos
    """
    return jsonify({
        'logs': webhook_logs,
        'count': len(webhook_logs),
        'timestamp': datetime.now().isoformat()
    }), 200

@stripe_webhook_bp.route('/webhook/clear-logs', methods=['POST'])
def clear_webhook_logs():
    """
    Limpa os logs dos webhooks
    """
    global webhook_logs
    webhook_logs = []
    
    log_webhook_event('ADMIN', 'Logs limpos')
    
    return jsonify({
        'status': 'success',
        'message': 'Logs cleared',
        'timestamp': datetime.now().isoformat()
    }), 200

@stripe_webhook_bp.route('/webhook/success', methods=['GET'])
def webhook_success():
    """
    Página de sucesso após pagamento
    """
    log_webhook_event('SUCCESS_PAGE', 'Página de sucesso acessada')
    
    return jsonify({
        'status': 'success',
        'message': 'Pagamento processado com sucesso!',
        'next_steps': [
            'Verifique seu email para confirmação',
            'Acesse sua conta para configurar suas credenciais',
            'Entre em contato conosco se tiver dúvidas'
        ],
        'timestamp': datetime.now().isoformat()
    })

@stripe_webhook_bp.route('/webhook/status', methods=['GET'])
def check_webhook_status():
    """
    Verifica status geral do webhook
    """
    log_webhook_event('STATUS_CHECK', 'Status do webhook verificado')
    
    return jsonify({
        'status': 'active',
        'message': 'Webhook funcionando corretamente',
        'webhook_secret_configured': STRIPE_WEBHOOK_SECRET != 'whsec_test_key',
        'webhook_secret_preview': STRIPE_WEBHOOK_SECRET[:20] + '...' if STRIPE_WEBHOOK_SECRET else 'NOT_SET',
        'logs_count': len(webhook_logs),
        'endpoints': [
            '/api/webhook/stripe - Recebe webhooks do Stripe',
            '/api/webhook/test - Endpoint de teste',
            '/api/webhook/logs - Visualizar logs dos webhooks',
            '/api/webhook/clear-logs - Limpar logs',
            '/api/webhook/success - Página de sucesso',
            '/api/webhook/status - Status do webhook'
        ],
        'timestamp': datetime.now().isoformat()
    })

@stripe_webhook_bp.route('/webhook/simulate', methods=['POST'])
def simulate_webhook():
    """
    Simula um webhook para testes
    """
    try:
        # Simular evento de checkout completado
        fake_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_simulate_' + str(datetime.now().timestamp()),
                    'customer_details': {
                        'email': 'teste@simulacao.com'
                    },
                    'payment_status': 'paid',
                    'amount_total': 5000
                }
            }
        }
        
        log_webhook_event('SIMULATION', 'Webhook simulado executado')
        
        # Processar como se fosse um webhook real
        event_type = fake_event['type']
        session = fake_event['data']['object']
        
        customer_email = session.get('customer_details', {}).get('email', '')
        session_id = session.get('id', '')
        
        log_webhook_event('SIMULATION_SUCCESS', f'Pagamento simulado para: {customer_email}')
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook simulation completed',
            'customer_email': customer_email,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        log_webhook_event('SIMULATION_ERROR', f'Erro na simulação: {str(e)}')
        return jsonify({'error': 'Simulation failed', 'details': str(e)}), 500 