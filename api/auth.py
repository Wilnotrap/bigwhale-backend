import logging
from flask import Blueprint, request, jsonify, session
from models.user import User
from database import db

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        email = data['email']
        password = data['password']
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        if not user.check_password(password):
            return jsonify({'success': False, 'message': 'Senha incorreta'}), 401
        
        if not user.is_active:
            return jsonify({'success': False, 'message': 'Usuário inativo'}), 403
        
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        user.last_login = db.func.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao fazer login: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'}), 500