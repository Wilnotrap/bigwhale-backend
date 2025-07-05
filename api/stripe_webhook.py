import stripe
from flask import Blueprint, request, jsonify, current_app
from ..models.user import User
from ..database import db
import os

stripe_webhook_bp = Blueprint('stripe_webhook_bp', __name__)

@stripe_webhook_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not endpoint_secret:
        current_app.logger.error('STRIPE_WEBHOOK_SECRET não configurado.')
        return jsonify(error={'message': 'Erro de configuração interno.'}), 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        current_app.logger.error(f'Erro no payload do webhook: {e}')
        return jsonify(error={'message': 'Payload inválido'}), 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f'Erro na verificação da assinatura: {e}')
        return jsonify(error={'message': 'Assinatura inválida'}), 400

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'checkout.session.completed':
        customer_email = data.get('customer_details', {}).get('email')
        stripe_customer_id = data.get('customer')
        if customer_email:
            user = User.query.filter_by(email=customer_email).first()
            if user:
                user.payment_status = 'completed'
                user.stripe_customer_id = stripe_customer_id
                db.session.commit()
                current_app.logger.info(f'Status de pagamento atualizado para {customer_email}')

    elif event_type == 'customer.subscription.created':
        stripe_customer_id = data.get('customer')
        subscription_id = data.get('id')
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
        if user:
            user.subscription_status = 'active'
            user.subscription_id = subscription_id
            db.session.commit()
            current_app.logger.info(f'Assinatura ativada para o cliente {stripe_customer_id}')

    elif event_type == 'customer.subscription.deleted':
        stripe_customer_id = data.get('customer')
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
        if user:
            user.subscription_status = 'canceled'
            db.session.commit()
            current_app.logger.info(f'Assinatura cancelada para o cliente {stripe_customer_id}')

    else:
        current_app.logger.info(f'Evento de webhook não tratado: {event_type}')

    return jsonify(status='success'), 200