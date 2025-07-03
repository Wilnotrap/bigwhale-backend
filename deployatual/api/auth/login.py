# backend/auth/login.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import request, jsonify, session, current_app
from models.user import User
from models.session import UserSession
from utils.security import decrypt_api_key
from api.bitget_client import BitgetAPI
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
import re
import sqlite3
import os
import uuid
from datetime import datetime

def ensure_admin_credentials():
    """Garante que as credenciais de admin estejam corretas"""
    try:
        # Credenciais padrão
        admin_users = [
            {
                'email': 'admin@bigwhale.com',
                'password': 'Raikamaster1@',
                'full_name': 'Admin BigWhale',
                'is_admin': True
            },
            {
                'email': 'willian@lexxusadm.com.br',
                'password': 'Bigwhale202021@',
                'full_name': 'Willian Admin',
                'is_admin': True
            }
        ]
        
        for admin_data in admin_users:
            user = User.query.filter_by(email=admin_data['email']).first()
            
            if user:
                # Atualizar senha e status de admin se necessário
                if not user.check_password(admin_data['password']):
                    user.password_hash = generate_password_hash(admin_data['password'])
                    user.is_active = True
                    current_app.logger.info(f"Senha atualizada para {admin_data['email']}")
                
                # Garantir que o status de admin esteja correto
                if user.is_admin != admin_data['is_admin']:
                    user.is_admin = admin_data['is_admin']
                    current_app.logger.info(f"Status de admin atualizado para {admin_data['email']}: {admin_data['is_admin']}")
            else:
                # Criar usuário se não existir
                user = User(
                    full_name=admin_data['full_name'],
                    email=admin_data['email'],
                    password_hash=generate_password_hash(admin_data['password']),
                    is_active=True,
                    is_admin=admin_data['is_admin']
                )
                db.session.add(user)
                current_app.logger.info(f"Usuário {admin_data['email']} criado")
        
        db.session.commit()
        return True
        
    except Exception as e:
        current_app.logger.error(f"Erro ao garantir credenciais admin: {e}")
        return False

def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'message': 'Email ou senha inválidos'}), 401

    if not user.is_active:
        return jsonify({'message': 'Conta desativada. Entre em contato com o suporte.'}), 403

    try:
        # Cria uma nova sessão usando o método da classe
        user_agent = request.headers.get('User-Agent')
        ip_address = request.remote_addr
        new_session = UserSession.create_session(
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address
        )

        # Descriptografa as credenciais da API
        api_key = decrypt_api_key(user.bitget_api_key_encrypted) if user.bitget_api_key_encrypted else None
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted) if user.bitget_api_secret_encrypted else None
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None

        # Verifica se as credenciais da API estão configuradas
        api_configured = bool(api_key and api_secret and passphrase)

        # Define os dados da sessão
        session['user_id'] = user.id
        session['session_token'] = new_session.session_token
        session.permanent = True

        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'bitget_api_key': api_key,
                'bitget_api_secret': api_secret,
                'bitget_passphrase': passphrase,
                'api_configured': api_configured,
                'session_token': new_session.session_token
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro durante o login: {str(e)}")
        return jsonify({'message': 'Erro interno no servidor'}), 500

def logout():
    """Endpoint para fazer logout"""
    try:
        # Obtém o token da sessão atual
        session_token = session.get('session_token')
        
        if session_token:
            # Busca e desativa a sessão
            user_session = UserSession.query.filter_by(session_token=session_token).first()
            if user_session:
                user_session.deactivate()
        
        # Limpa a sessão do Flask
        session.clear()
        
        return jsonify({'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        print(f"Erro durante o logout: {str(e)}")
        return jsonify({'message': 'Erro ao fazer logout'}), 500

def check_session():
    """Verifica se a sessão está ativa"""
    try:
        # Obtém o token da sessão atual
        session_token = session.get('session_token')
        
        if not session_token:
            return jsonify({'authenticated': False}), 200
            
        # Busca a sessão ativa
        user_session = UserSession.get_active_session(session_token)
        
        if not user_session:
            session.clear()
            return jsonify({'authenticated': False}), 200
            
        # Busca o usuário
        user = User.query.get(user_session.user_id)
        
        if not user or not user.is_active:
            session.clear()
            return jsonify({'authenticated': False}), 200
            
        # Descriptografa as credenciais da API
        api_key = decrypt_api_key(user.bitget_api_key_encrypted) if user.bitget_api_key_encrypted else None
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted) if user.bitget_api_secret_encrypted else None
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
        
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'bitget_api_key': api_key,
                'bitget_api_secret': api_secret,
                'bitget_passphrase': passphrase,
                'api_configured': bool(api_key and api_secret and passphrase)
            }
        }), 200
    except Exception as e:
        print(f"Erro ao verificar sessão: {str(e)}")
        return jsonify({'authenticated': False, 'error': str(e)}), 500