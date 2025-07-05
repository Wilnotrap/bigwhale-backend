from flask import Blueprint, request, jsonify, session
from models.user import User
from models.trade import Trade
from database import db
from utils.security import decrypt_api_key
from api.bitget_client import BitgetAPI
from datetime import datetime
import json
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dashboard_bp = Blueprint('dashboard', __name__)

def require_login(f):
    """Decorator para verificar se o usuário está logado"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Login necessário'}), 401
        
        session.permanent = True
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@dashboard_bp.route('/stats', methods=['GET'])
@require_login
def get_user_stats():
    """Retorna estatísticas do usuário"""
    try:
        user_id = session['user_id']
        
        stats = {
            'realized_pnl': 0,
            'unrealized_pnl': 0,
            'margin_size': 0,
            'open_positions_count': 0,
            'total_pnl': 0,
            'win_rate': 0,
            'total_trades': 0,
            'winning_trades': 0,
        }
        
        # Calcular estatísticas básicas do banco de dados
        closed_trades = Trade.query.filter_by(user_id=user_id, status='closed').all()
        open_trades = Trade.query.filter_by(user_id=user_id, status='open').all()
        
        stats['total_trades'] = len(closed_trades)
        stats['open_positions_count'] = len(open_trades)
        
        if closed_trades:
            total_pnl = sum(trade.pnl or 0 for trade in closed_trades)
            winning_trades = sum(1 for trade in closed_trades if (trade.pnl or 0) > 0)
            
            stats['realized_pnl'] = total_pnl
            stats['winning_trades'] = winning_trades
            stats['win_rate'] = (winning_trades / len(closed_trades)) * 100 if closed_trades else 0
        
        if open_trades:
            stats['unrealized_pnl'] = sum(trade.pnl or 0 for trade in open_trades)
        
        stats['total_pnl'] = stats['realized_pnl'] + stats['unrealized_pnl']
        
        return jsonify({'success': True, 'data': stats}), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'message': 'Erro ao carregar estatísticas'}), 500

@dashboard_bp.route('/trades/open', methods=['GET'])
@require_login
def get_open_trades():
    """Retorna trades abertos do usuário"""
    try:
        user_id = session['user_id']
        open_trades = Trade.query.filter_by(user_id=user_id, status='open').all()
        
        trades_data = [trade.to_dict() for trade in open_trades]
        return jsonify({
            'success': True,
            'data': trades_data
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter trades abertos: {str(e)}")
        return jsonify({'message': 'Erro ao carregar trades abertos'}), 500

@dashboard_bp.route('/trades/closed', methods=['GET'])
@require_login
def get_closed_trades():
    """Retorna trades fechados do usuário"""
    try:
        user_id = session['user_id']
        closed_trades = Trade.query.filter_by(user_id=user_id, status='closed').all()
        
        trades_data = [trade.to_dict() for trade in closed_trades]
        return jsonify({
            'success': True,
            'data': trades_data
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter trades fechados: {str(e)}")
        return jsonify({'message': 'Erro ao carregar trades fechados'}), 500