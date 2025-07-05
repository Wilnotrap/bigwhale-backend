from flask import Blueprint, request, jsonify
from functools import wraps
from models.user import User
from models.trade import Trade
from database import db
from datetime import datetime
from sqlalchemy import func, desc, case
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin_clean', __name__)

def admin_required(f):
    @wraps(f) 
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'user_id' not in session:
            return jsonify({'message': 'Acesso negado'}), 403
            
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'message': 'Acesso de administrador necessário'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        users_query = User.query.filter_by(is_active=True)
        
        pagination = users_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in pagination.items:
            users_data.append({
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'operational_balance': user.operational_balance or 0,
                'operational_balance_usd': user.operational_balance_usd or 0
            })
        
        summary = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'inactive_users': User.query.filter_by(is_active=False).count(),
            'admin_users': User.query.filter_by(is_admin=True).count()
        }
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            },
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter usuários: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_admin_dashboard_stats():
    """Obter estatísticas gerais do dashboard admin."""
    try:
        total_users = db.session.query(func.count(User.id)).scalar()
        active_users = db.session.query(func.count(User.id)).filter_by(is_active=True).scalar()
        admin_users = db.session.query(func.count(User.id)).filter_by(is_admin=True).scalar()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do dashboard admin: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500