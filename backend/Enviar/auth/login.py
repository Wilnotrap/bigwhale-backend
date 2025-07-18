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
    try:
        current_app.logger.info("=== INÍCIO DO PROCESSO DE LOGIN ===")
        
        # Verificar se a requisição contém JSON
        if not request.is_json:
            current_app.logger.error("Requisição não contém JSON válido")
            return jsonify({'message': 'Content-Type deve ser application/json'}), 400
            
        data = request.get_json()
        if not data:
            current_app.logger.error("Dados JSON vazios ou inválidos")
            return jsonify({'message': 'Dados JSON inválidos'}), 400
            
        current_app.logger.info(f"Dados recebidos: {list(data.keys()) if data else 'None'}")
        
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            current_app.logger.warning(f"Campos obrigatórios ausentes - Email: {bool(email)}, Password: {bool(password)}")
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400

        current_app.logger.info(f"Tentativa de login para email: {email}")
        
        # Buscar usuário no banco
        try:
            user = User.query.filter_by(email=email).first()
            current_app.logger.info(f"Usuário encontrado: {bool(user)}")
        except Exception as db_error:
            current_app.logger.error(f"Erro ao buscar usuário no banco: {str(db_error)}")
            return jsonify({'message': 'Erro interno no servidor - banco de dados'}), 500

        if not user:
            current_app.logger.warning(f"Usuário não encontrado: {email}")
            return jsonify({'message': 'Email ou senha inválidos'}), 401
            
        # Verificar senha
        try:
            password_valid = user.check_password(password)
            current_app.logger.info(f"Senha válida: {password_valid}")
        except Exception as pwd_error:
            current_app.logger.error(f"Erro ao verificar senha: {str(pwd_error)}")
            return jsonify({'message': 'Erro interno no servidor - autenticação'}), 500
            
        if not password_valid:
            current_app.logger.warning(f"Senha inválida para usuário: {email}")
            return jsonify({'message': 'Email ou senha inválidos'}), 401

        if not user.is_active:
            current_app.logger.warning(f"Usuário inativo: {email}")
            return jsonify({'message': 'Conta desativada. Entre em contato com o suporte.'}), 403

        current_app.logger.info("Credenciais validadas com sucesso")
        
        # Criar nova sessão
        try:
            user_agent = request.headers.get('User-Agent', 'Unknown')
            ip_address = request.remote_addr or 'Unknown'
            current_app.logger.info(f"Criando sessão - User Agent: {user_agent[:50]}..., IP: {ip_address}")
            
            new_session = UserSession.create_session(
                user_id=user.id,
                user_agent=user_agent,
                ip_address=ip_address
            )
            current_app.logger.info(f"Sessão criada com sucesso - ID: {new_session.id}")
            
        except Exception as session_error:
            current_app.logger.error(f"Erro ao criar sessão: {str(session_error)}")
            db.session.rollback()
            return jsonify({'message': 'Erro interno no servidor - sessão'}), 500

        # Descriptografar credenciais da API
        api_key = None
        api_secret = None
        passphrase = None
        
        try:
            current_app.logger.info("Iniciando descriptografia de credenciais")
            
            if user.bitget_api_key_encrypted:
                api_key = decrypt_api_key(user.bitget_api_key_encrypted)
                current_app.logger.info(f"API Key descriptografada: {bool(api_key)}")
            
            if user.bitget_api_secret_encrypted:
                api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
                current_app.logger.info(f"API Secret descriptografado: {bool(api_secret)}")
                
            if user.bitget_passphrase_encrypted:
                passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)
                current_app.logger.info(f"Passphrase descriptografado: {bool(passphrase)}")
                
        except Exception as decrypt_error:
            current_app.logger.error(f"Erro na descriptografia: {str(decrypt_error)}")
            # Não falhar o login por erro de descriptografia
            api_key = None
            api_secret = None
            passphrase = None

        # Verificar se as credenciais da API estão configuradas
        api_configured = bool(api_key and api_secret and passphrase)
        current_app.logger.info(f"API configurada: {api_configured}")

        # Definir dados da sessão Flask
        try:
            session['user_id'] = user.id
            session['session_token'] = new_session.session_token
            session.permanent = True
            current_app.logger.info("Sessão Flask configurada")
        except Exception as flask_session_error:
            current_app.logger.error(f"Erro ao configurar sessão Flask: {str(flask_session_error)}")
            # Continuar mesmo com erro na sessão Flask

        # Preparar resposta
        response_data = {
            'message': 'Login realizado com sucesso',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'api_configured': api_configured,
                'session_token': new_session.session_token,
                'bitget_api_key': api_key,
                'bitget_api_secret': api_secret,
                'bitget_passphrase': passphrase
            }
        }
        
        current_app.logger.info("=== LOGIN CONCLUÍDO COM SUCESSO ===")
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error("=== ERRO CRÍTICO NO LOGIN ===")
        current_app.logger.error(f"Tipo do erro: {type(e).__name__}")
        current_app.logger.error(f"Mensagem: {str(e)}")
        
        # Log do traceback completo
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        try:
            db.session.rollback()
        except:
            pass
            
        return jsonify({
            'message': 'Erro interno no servidor',
            'error_type': type(e).__name__,
            'debug_info': str(e) if current_app.debug else None
        }), 500

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
            
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }
        }), 200
    except Exception as e:
        print(f"Erro ao verificar sessão: {str(e)}")
        return jsonify({'authenticated': False, 'error': str(e)}), 500