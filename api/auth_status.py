#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints para verificar status de autenticação e pagamento
"""

from flask import Blueprint, request, jsonify, session
from database import db
from models.user import User
from models.session import UserSession
import logging

# Configurar blueprint
auth_status_bp = Blueprint('auth_status', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

@auth_status_bp.route('/api/auth/check-payment-status', methods=['POST'])
def check_payment_status():
    """
    Verifica se o usuário foi ativado após pagamento
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email é obrigatório'}), 400
        
        # Buscar usuário pelo email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'status': 'not_found',
                'message': 'Usuário não encontrado'
            }), 404
        
        # Verificar se está ativo
        if user.is_active and user.subscription_status == 'active':
            return jsonify({
                'status': 'active',
                'message': 'Usuário ativo e pronto para usar',
                'user_id': user.id,
                'subscription_status': user.subscription_status
            }), 200
        elif user.subscription_status == 'incomplete':
            return jsonify({
                'status': 'incomplete',
                'message': 'Pagamento em processamento'
            }), 202
        else:
            return jsonify({
                'status': 'inactive',
                'message': 'Usuário ainda não ativado'
            }), 200
            
    except Exception as e:
        logger.error(f"Erro ao verificar status de pagamento: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_status_bp.route('/api/auth/activate-after-payment', methods=['POST'])
def activate_after_payment():
    """
    Ativa o usuário após confirmação de pagamento
    """
    try:
        data = request.get_json()
        email = data.get('email')
        subscription_id = data.get('subscription_id')
        
        if not email:
            return jsonify({'error': 'Email é obrigatório'}), 400
        
        # Buscar usuário pelo email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se já está ativo
        if user.is_active and user.subscription_status == 'active':
            return jsonify({
                'status': 'already_active',
                'message': 'Usuário já está ativo'
            }), 200
        
        # Ativar usuário
        user.is_active = True
        user.subscription_status = 'active'
        
        if subscription_id:
            user.subscription_id = subscription_id
        
        db.session.commit()
        
        # Criar sessão para o usuário
        try:
            # Remover sessões antigas
            UserSession.query.filter_by(user_id=user.id).delete()
            
            # Criar nova sessão
            session_token = f"payment_activated_{user.id}"
            user_session = UserSession(
                user_id=user.id,
                session_token=session_token,
                is_active=True
            )
            db.session.add(user_session)
            db.session.commit()
            
            # Definir na sessão Flask
            session['user_id'] = user.id
            session['email'] = user.email
            session['is_active'] = True
            
        except Exception as session_error:
            logger.error(f"Erro ao criar sessão: {str(session_error)}")
            # Continuar mesmo se não conseguir criar sessão
        
        return jsonify({
            'status': 'activated',
            'message': 'Usuário ativado com sucesso',
            'user_id': user.id,
            'redirect_to': 'dashboard'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao ativar usuário: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_status_bp.route('/api/auth/subscription-status/<int:user_id>', methods=['GET'])
def get_subscription_status(user_id):
    """
    Obtém o status da assinatura do usuário
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user_id': user.id,
            'email': user.email,
            'is_active': user.is_active,
            'subscription_status': user.subscription_status,
            'subscription_id': user.subscription_id
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter status da assinatura: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500 