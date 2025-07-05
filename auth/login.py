from flask import request, jsonify, session
from werkzeug.security import check_password_hash
from models.user import User
import logging

logger = logging.getLogger(__name__)

def login():
    """Função de login do usuário"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                return jsonify({'message': 'Conta desativada'}), 403
            
            session['user_id'] = user.id
            session['user_email'] = user.email
            session.permanent = True
            
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_admin': user.is_admin
                }
            }), 200
        else:
            return jsonify({'message': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

def logout():
    """Função de logout do usuário"""
    try:
        session.clear()
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"Erro no logout: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

def check_session():
    """Verifica se o usuário está logado"""
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_active:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_admin': user.is_admin
                    }
                }), 200
        
        return jsonify({'authenticated': False}), 401
        
    except Exception as e:
        logger.error(f"Erro ao verificar sessão: {str(e)}")
        return jsonify({'authenticated': False}), 401