from flask import Blueprint, request, jsonify, current_app
import stripe
import os
import logging
from datetime import datetime, timedelta
from models.user import User
from database import db

# Configuração de logging
logger = logging.getLogger(__name__)

# Criar blueprint para webhooks da Stripe
stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

# No início da função webhook
@stripe_webhook_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    current_app.logger.info(f"🔔 [{timestamp}] Webhook Stripe recebido!")
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    # Obter o segredo do webhook das variáveis de ambiente
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET não configurado nas variáveis de ambiente.")
        return jsonify({'error': 'Webhook secret not configured'}), 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Erro no payload do webhook da Stripe: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Erro na verificação da assinatura do webhook da Stripe: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"Erro inesperado no webhook da Stripe: {e}")
        return jsonify({'error': 'Unexpected error'}), 500

    # Processar eventos da Stripe
    # Adicionar verificações extras de segurança
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Verificações de segurança
        payment_status = session.get('payment_status')
        payment_intent_status = session.get('payment_intent', {}).get('status') if isinstance(session.get('payment_intent'), dict) else None
        customer_email = session.get('customer_details', {}).get('email')
        amount_total = session.get('amount_total', 0)
        
        logger.info(f"📊 Webhook recebido - Email: {customer_email}, Payment Status: {payment_status}, Amount: {amount_total}")
        
        # ✅ MÚLTIPLAS VERIFICAÇÕES DE SEGURANÇA
        if (payment_status == 'paid' and 
            customer_email and 
            amount_total > 0 and
            '@' in customer_email):  # Validação básica de email
            
            # Verificação adicional do payment_intent se disponível
            if payment_intent_status and payment_intent_status != 'succeeded':
                logger.warning(f"❌ Payment intent não succeeded: {payment_intent_status}")
                return jsonify({'status': 'payment_not_succeeded'}), 200
            
            try:
                user = User.query.filter_by(email=customer_email).first()
                if user:
                    # Verificar se já não foi processado (evitar duplicação)
                    if user.has_paid and user.subscription_end_date and user.subscription_end_date > datetime.utcnow():
                        logger.info(f"⚠️ Usuário {customer_email} já possui assinatura ativa")
                        return jsonify({'status': 'already_processed'}), 200
                    
                    # Determinar tipo de assinatura baseado no valor
                    subscription_type = 'monthly'
                    duration_days = 30
                    
                    # Valores em centavos (Stripe)
                    if amount_total >= 50000:  # R$ 500,00 ou mais = anual
                        subscription_type = 'annual'
                        duration_days = 365
                    elif amount_total >= 5000:  # R$ 50,00 = mensal
                        subscription_type = 'monthly'
                        duration_days = 30
                    else:
                        logger.warning(f"❌ Valor muito baixo: {amount_total}")
                        return jsonify({'status': 'invalid_amount'}), 200
                    
                    # Atualizar usuário
                    user.has_paid = True
                    user.subscription_type = subscription_type
                    user.subscription_start_date = datetime.utcnow()
                    user.subscription_end_date = datetime.utcnow() + timedelta(days=duration_days)
                    user.stripe_customer_id = session.get('customer')
                    
                    db.session.commit()
                    
                    logger.info(f"✅ SUCESSO: Usuário {customer_email} liberado - Tipo: {subscription_type}, Valor: R$ {amount_total/100:.2f}")
                    
                else:
                    logger.error(f"❌ Usuário não encontrado: {customer_email}")
                    return jsonify({'status': 'user_not_found'}), 404
                    
            except Exception as e:
                db.session.rollback()
                logger.error(f"❌ ERRO CRÍTICO ao processar pagamento: {e}")
                return jsonify({'status': 'processing_error'}), 500
        else:
            # Log detalhado para pagamentos rejeitados
            logger.warning(f"❌ PAGAMENTO REJEITADO - Status: {payment_status}, Email: {customer_email}, Amount: {amount_total}")
            return jsonify({'status': 'payment_rejected'}), 200

    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        
        # Buscar usuário pelo customer_id da Stripe
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.stripe_subscription_id = subscription.get('id')
            db.session.commit()
            logger.info(f"Subscription ID atualizado para usuário {user.email}")
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription.get('id')
        
        # Cancelar assinatura do usuário
        user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
        if user:
            user.has_paid = False
            user.subscription_end_date = datetime.utcnow()
            db.session.commit()
            logger.info(f"Assinatura cancelada para usuário {user.email}")

    # Log final de sucesso
    current_app.logger.info(f"✅ [{timestamp}] Webhook processado com sucesso")
    return jsonify({
        'status': 'success', 
        'timestamp': timestamp,
        'processed': True
    }), 200