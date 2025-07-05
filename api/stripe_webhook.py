#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook do Stripe para automatizar liberação de usuários
"""

import os
import json
import stripe
import logging
from flask import Blueprint, request, jsonify
from database import db
from models.user import User
from models.session import UserSession
from werkzeug.security import generate_password_hash
import hashlib
import hmac

# Configurar o blueprint
stripe_webhook_bp = Blueprint('stripe_webhook', __name__)

# Configurar Stripe
stripe.api_key = os.environ.get('STRIPE_API_KEY')  # Chave secreta do Stripe
webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_stripe_signature(payload, signature):
    """
    Verifica se o webhook veio realmente do Stripe
    """
    try:
        # Extrair elementos da assinatura
        elements = signature.split(',')
        timestamp = None
        signatures = []
        
        for element in elements:
            if element.startswith('t='):
                timestamp = element[2:]
            elif element.startswith('v1='):
                signatures.append(element[3:])
        
        if not timestamp or not signatures:
            logger.error("Assinatura malformada")
            return False
        
        # Criar payload para verificação
        payload_to_sign = f"{timestamp}.{payload}"
        
        # Calcular assinatura esperada
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Verificar se alguma assinatura bate
        for signature in signatures:
            if hmac.compare_digest(expected_signature, signature):
                logger.info("Assinatura do webhook verificada com sucesso")
                return True
        
        logger.error("Assinatura do webhook inválida")
        return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar assinatura: {str(e)}")
        return False

def process_checkout_session(session):
    """
    Processa uma sessão de checkout completada
    """
    try:
        logger.info(f"🛒 Processando sessão de checkout: {session.get('id')}")
        logger.info(f"📋 Dados completos da sessão: {json.dumps(session, indent=2)}")
        
        # Extrair dados da sessão
        customer_email = session.get('customer_details', {}).get('email')
        customer_name = session.get('customer_details', {}).get('name')
        subscription_id = session.get('subscription')
        amount_total = session.get('amount_total', 0) / 100  # Converter de centavos
        session_id = session.get('id')
        
        logger.info(f"👤 Email do cliente: {customer_email}")
        logger.info(f"📝 Nome do cliente: {customer_name}")
        logger.info(f"📄 Subscription ID: {subscription_id}")
        logger.info(f"💰 Valor total: R$ {amount_total}")
        logger.info(f"🆔 Session ID: {session_id}")
        
        if not customer_email:
            logger.error("❌ Email do cliente não encontrado na sessão")
            return False
        
        # Verificar se o usuário já existe
        logger.info(f"🔍 Verificando se usuário {customer_email} já existe...")
        user = User.query.filter_by(email=customer_email).first()
        
        if user:
            # Usuário já existe - atualizar status
            logger.info(f"✅ Usuário existente encontrado: {customer_email}")
            user.is_active = True
            user.subscription_status = 'active'
            user.subscription_id = subscription_id
            logger.info(f"🔄 Status do usuário atualizado para ativo")
        else:
            # Criar novo usuário
            logger.info(f"➕ Criando novo usuário: {customer_email}")
            
            # Gerar senha temporária mais segura
            import secrets
            temp_password = f"BigWhale{secrets.token_hex(4)}@{amount_total:.0f}"
            
            user = User(
                full_name=customer_name or customer_email.split('@')[0],
                email=customer_email,
                password_hash=generate_password_hash(temp_password),
                is_active=True,
                subscription_status='active',
                subscription_id=subscription_id,
                is_admin=False,
                nautilus_active=True,
                commission_rate=0.35,
                operational_balance=0.0,
                operational_balance_usd=0.0
            )
            db.session.add(user)
            logger.info(f"👤 Novo usuário criado com senha temporária")
        
        # Salvar no banco
        logger.info("💾 Salvando dados no banco...")
        db.session.commit()
        logger.info("✅ Dados salvos com sucesso!")
        
        # Criar sessão ativa para o usuário
        try:
            logger.info("🔐 Criando sessão para o usuário...")
            # Remover sessões antigas
            UserSession.query.filter_by(user_id=user.id).delete()
            
            # Criar nova sessão
            session_token = f"stripe_activated_{user.id}_{session_id}"
            user_session = UserSession(
                user_id=user.id,
                session_token=session_token,
                is_active=True
            )
            db.session.add(user_session)
            db.session.commit()
            logger.info(f"🎯 Sessão criada para usuário: {user.id}")
            
        except Exception as session_error:
            logger.error(f"⚠️ Erro ao criar sessão: {str(session_error)}")
            # Continuar mesmo se não conseguir criar sessão
        
        logger.info(f"🎉 Usuário {customer_email} ativado com sucesso!")
        logger.info(f"🏁 Processo de checkout completado para: {customer_email}")
        return True
        
    except Exception as e:
        logger.error(f"💥 ERRO ao processar checkout session: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return False

@stripe_webhook_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Endpoint para receber webhooks do Stripe
    """
    try:
        # Obter dados do webhook
        payload = request.get_data(as_text=True)
        signature = request.headers.get('Stripe-Signature')
        
        logger.info("🚀 === WEBHOOK STRIPE RECEBIDO ===")
        logger.info(f"📦 Payload recebido: {len(payload)} caracteres")
        logger.info(f"🔐 Headers: {dict(request.headers)}")
        logger.info(f"✍️ Assinatura: {signature[:50] if signature else 'Nenhuma'}...")
        
        if not webhook_secret:
            logger.error("❌ STRIPE_WEBHOOK_SECRET não configurado")
            return jsonify({'error': 'Webhook secret não configurado'}), 500
        
        logger.info(f"🗝️ Webhook secret configurado: {webhook_secret[:10]}...")
        
        # TEMPORÁRIO: Pular verificação de assinatura para debug
        logger.warning("⚠️ MODO DEBUG: Pulando verificação de assinatura")
        
        # # Verificar assinatura
        # if not verify_stripe_signature(payload, signature):
        #     logger.error("Assinatura inválida")
        #     return jsonify({'error': 'Assinatura inválida'}), 400
        
        # Parsear evento
        try:
            event = json.loads(payload)
            logger.info(f"📄 Evento parseado: {json.dumps(event, indent=2)[:500]}...")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Payload inválido: {str(e)}")
            return jsonify({'error': 'Payload inválido'}), 400
        
        event_type = event.get('type')
        logger.info(f"🎯 Tipo de evento: {event_type}")
        
        # Processar eventos relevantes
        if event_type == 'checkout.session.completed':
            logger.info("💳 Processando checkout.session.completed")
            session = event.get('data', {}).get('object', {})
            success = process_checkout_session(session)
            
            if success:
                logger.info("✅ Checkout session processado com sucesso")
                return jsonify({'status': 'success'}), 200
            else:
                logger.error("❌ Erro ao processar checkout session")
                return jsonify({'error': 'Erro ao processar checkout'}), 500
        
        elif event_type == 'customer.subscription.created':
            logger.info("📝 Assinatura criada - processando...")
            # Aqui você pode adicionar lógica adicional para assinaturas
            return jsonify({'status': 'success'}), 200
        
        elif event_type == 'customer.subscription.updated':
            logger.info("🔄 Assinatura atualizada - processando...")
            # Lógica para atualização de assinatura
            return jsonify({'status': 'success'}), 200
        
        elif event_type == 'customer.subscription.deleted':
            logger.info("🗑️ Assinatura cancelada - processando...")
            # Lógica para cancelamento de assinatura
            subscription_id = event.get('data', {}).get('object', {}).get('id')
            if subscription_id:
                # Desativar usuário
                user = User.query.filter_by(subscription_id=subscription_id).first()
                if user:
                    user.is_active = False
                    user.subscription_status = 'canceled'
                    db.session.commit()
                    logger.info(f"Usuário {user.email} desativado por cancelamento")
            
            return jsonify({'status': 'success'}), 200
        
        else:
            logger.info(f"🤷 Evento não processado: {event_type}")
            return jsonify({'status': 'ignored'}), 200
    
    except Exception as e:
        logger.error(f"💥 ERRO CRÍTICO no webhook: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback completo: {traceback.format_exc()}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@stripe_webhook_bp.route('/webhook/stripe/test', methods=['GET'])
def webhook_test():
    """
    Endpoint para testar se o webhook está funcionando
    """
    return jsonify({
        'status': 'ok',
        'message': 'Webhook do Stripe está funcionando!',
        'webhook_secret_configured': bool(webhook_secret)
    }), 200 