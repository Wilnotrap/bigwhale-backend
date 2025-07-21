import logging
from flask import Blueprint, request, jsonify, session
from models.user import User
from services.demo_bitget_api import get_demo_api

logger = logging.getLogger(__name__)
demo_trading_bp = Blueprint('demo_trading', __name__)

def require_demo_auth(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login necessário'}), 401
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        if user.email != 'financeiro@lexxusadm.com.br':
            return jsonify({'success': False, 'message': 'Acesso negado - apenas conta demo'}), 403
        
        return f(user_id, user, *args, **kwargs)
    
    return decorated_function

@demo_trading_bp.route('/demo/balance', methods=['GET'])
@require_demo_auth
def get_demo_balance(user_id, user):
    try:
        demo_api = get_demo_api(user_id)
        balance_data = demo_api.get_account_balance()
        return jsonify(balance_data), 200
    except Exception as e:
        logger.error(f"Erro ao obter saldo demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@demo_trading_bp.route('/demo/positions', methods=['GET'])
@require_demo_auth
def get_demo_positions(user_id, user):
    try:
        demo_api = get_demo_api(user_id)
        positions_data = demo_api.get_positions()
        return jsonify(positions_data), 200
    except Exception as e:
        logger.error(f"Erro ao obter posições demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@demo_trading_bp.route('/demo/stats', methods=['GET'])
@require_demo_auth
def get_demo_stats(user_id, user):
    try:
        demo_api = get_demo_api(user_id)
        stats_data = demo_api.get_trading_stats()
        return jsonify(stats_data), 200
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas demo: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500