from flask import Blueprint, request, jsonify, current_app
import stripe
import os
import logging
from models.user import User
from database import db

# Configuração de logging
logger = logging.getLogger(__name__)

# Criar blueprint para webhooks da Stripe
stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

@stripe_webhook_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    current_app.logger.info("Webhook da Stripe recebido!")
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    # Obter o segredo do webhook das variáveis de ambiente
    # IMPORTANTE: Você precisará adicionar STRIPE_WEBHOOK_SECRET no painel do Render!
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET não configurado nas variáveis de ambiente.")
        return jsonify({'error': 'Webhook secret not configured'}), 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Erro no payload do webhook da Stripe: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Erro na verificação da assinatura do webhook da Stripe: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"Erro inesperado no webhook da Stripe: {e}")
        return jsonify({'error': 'Unexpected error'}), 500

    # Lidar com o evento (payment_intent.succeeded, checkout.session.completed, etc.)
    if event['type'] == 'checkout.session.completed':
        session_id = event['data']['object']['id']
        customer_email = event['data']['object'].get('customer_details', {}).get('email')
        payment_status = event['data']['object']['payment_status']

        logger.info(f"Evento checkout.session.completed recebido para sessão: {session_id} com email: {customer_email} e status: {payment_status}")

        # Se o pagamento foi bem-sucedido, atualizar o status do usuário no banco de dados
        if payment_status == 'paid' and customer_email:
            try:
                user = User.query.filter_by(email=customer_email).first()
                if user:
                    user.has_paid = True # Ou user.is_premium = True, etc.
                    db.session.commit()
                    logger.info(f"Usuário {customer_email} atualizado para status de pago com sucesso.")
                    # AQUI: Adicione qualquer lógica adicional para liberar acesso ao Nautilus
                    # Por exemplo, uma chamada para nautilus_service.enable_user_access(user.id)
                else:
                    logger.warning(f"Usuário com email {customer_email} não encontrado para evento de pagamento.")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Erro ao atualizar status do usuário {customer_email} no banco de dados: {e}")
                return jsonify({'error': 'Database update failed'}), 500
        else:
            logger.warning(f"Pagamento não concluído ou email do cliente não disponível para sessão: {session_id}")

    elif event['type'] == 'customer.subscription.created':
        # Exemplo de como lidar com outros eventos, como criação de assinatura
        logger.info(f"Evento customer.subscription.created recebido para assinatura: {event['data']['object']['id']}")
        # Lógica para registrar nova assinatura
    # Adicione mais 'elif' para outros tipos de eventos que você configurou

    return jsonify({'status': 'success'}), 200 