#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API endpoints para trading demo - Versão corrigida
"""

from flask import Blueprint, request, jsonify, current_app, session
from models.user import User
from database import db

demo_trading_bp = Blueprint('demo_trading', __name__)

def require_demo_auth(f):
    """Decorator simples para autenticação da conta demo"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login necessário'}), 401
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        # Verificar se é a conta demo
        if user.email != 'financeiro@lexxusadm.com.br':
            return jsonify({'success': False, 'message': 'Acesso negado - apenas conta demo'}), 403
        
        return f(user_id, user, *args, **kwargs)
    
    return decorated_function

@demo_trading_bp.route('/demo/balance', methods=['GET'])
@require_demo_auth
def get_demo_balance(user_id, user):
    """Retorna saldo da conta demo"""
    try:
        from services.demo_bitget_api import get_demo_api
        
        # Obter API demo
        demo_api = get_demo_api(user_id)
        balance_data = demo_api.get_account_balance()
        
        return jsonify(balance_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter saldo demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@demo_trading_bp.route('/demo/positions', methods=['GET'])
@require_demo_auth
def get_demo_positions(user_id, user):
    """Retorna posições da conta demo"""
    try:
        from services.demo_bitget_api import get_demo_api
        
        # Obter API demo
        demo_api = get_demo_api(user_id)
        positions_data = demo_api.get_positions()
        
        return jsonify(positions_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter posições demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@demo_trading_bp.route('/demo/stats', methods=['GET'])
@require_demo_auth
def get_demo_stats(user_id, user):
    """Retorna estatísticas de trading da conta demo"""
    try:
        from services.demo_bitget_api import get_demo_api
        
        # Obter API demo
        demo_api = get_demo_api(user_id)
        stats_data = demo_api.get_trading_stats()
        
        return jsonify(stats_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@demo_trading_bp.route('/demo/execute-signal', methods=['POST'])
@require_demo_auth
def execute_demo_signal(user_id, user):
    """Executa um sinal na conta demo"""
    try:
        # Obter dados do sinal
        signal_data = request.get_json()
        if not signal_data:
            return jsonify({'success': False, 'message': 'Dados do sinal não fornecidos'}), 400
        
        from services.demo_bitget_api import get_demo_api
        
        # Obter API demo
        demo_api = get_demo_api(user_id)
        result = demo_api.simulate_signal_execution(signal_data)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao executar sinal demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@demo_trading_bp.route('/demo/close-position', methods=['POST'])
@require_demo_auth
def close_demo_position(user_id, user):
    """Fecha uma posição na conta demo"""
    try:
        # Obter dados da requisição
        data = request.get_json()
        if not data or 'position_id' not in data:
            return jsonify({'success': False, 'message': 'ID da posição não fornecido'}), 400
        
        position_id = data['position_id']
        close_price = data.get('price')
        
        from services.demo_bitget_api import get_demo_api
        
        # Obter API demo
        demo_api = get_demo_api(user_id)
        result = demo_api.close_position(position_id, close_price)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao fechar posição demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@demo_trading_bp.route('/demo/place-order', methods=['POST'])
@require_demo_auth
def place_demo_order(user_id, user):
    """Coloca uma ordem na conta demo"""
    try:
        # Obter dados da ordem
        order_data = request.get_json()
        if not order_data:
            return jsonify({'success': False, 'message': 'Dados da ordem não fornecidos'}), 400
        
        required_fields = ['symbol', 'side', 'size']
        for field in required_fields:
            if field not in order_data:
                return jsonify({'success': False, 'message': f'Campo obrigatório: {field}'}), 400
        
        from services.demo_bitget_api import get_demo_api
        
        # Obter API demo
        demo_api = get_demo_api(user_id)
        result = demo_api.place_order(
            symbol=order_data['symbol'],
            side=order_data['side'],
            size=float(order_data['size']),
            price=order_data.get('price'),
            order_type=order_data.get('type', 'market'),
            leverage=int(order_data.get('leverage', 1))
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao colocar ordem demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500