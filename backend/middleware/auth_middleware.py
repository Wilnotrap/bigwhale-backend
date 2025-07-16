#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de autenticação robusto
Garante que o sistema de login funcione sem erros recorrentes
"""

# import sqlite3  # Removido - usando apenas PostgreSQL
import os
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from database import db

class AuthMiddleware:
    """Middleware para gerenciar autenticação de forma robusta"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o middleware com a aplicação Flask"""
        # app.before_first_request(self.ensure_admin_users)  # Removido
        app.before_request(self.validate_auth_request)
    
    def ensure_admin_users(self):
        """Garante que os usuários admin existam e tenham credenciais corretas"""
        
        try:
            with current_app.app_context():
                # Verificar se os usuários admin existem
                admin_users = [
                    {
                        'email': 'admin@bigwhale.com',
                        'password': 'bigwhale123',
                        'full_name': 'Admin BigWhale',
                        'is_admin': False
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
                        # Atualizar usuário existente
                        user.password_hash = generate_password_hash(admin_data['password'])
                        user.is_active = True
                        user.is_admin = admin_data['is_admin']
                        current_app.logger.info(f"Usuário {admin_data['email']} atualizado")
                    else:
                        # Criar novo usuário
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
                current_app.logger.info("Usuários admin configurados com sucesso")
                
        except Exception as e:
            current_app.logger.error(f"Erro ao configurar usuários admin: {e}")
            # Tentar configuração direta no banco
            self._direct_db_setup()
    
    def _direct_db_setup(self):
        """Configuração direta no banco PostgreSQL usando SQLAlchemy como fallback"""
        
        try:
            current_app.logger.info("Tentando configuração direta via SQLAlchemy...")
            
            # Configurar usuários admin usando SQLAlchemy
            admin_users = [
                ('admin@bigwhale.com', 'bigwhale123', 'Admin BigWhale', False),
                ('willian@lexxusadm.com.br', 'Bigwhale202021@', 'Willian Admin', True)
            ]
            
            for email, password, full_name, is_admin in admin_users:
                password_hash = generate_password_hash(password)
                
                # Verificar se usuário existe
                user = User.query.filter_by(email=email).first()
                
                if user:
                    # Atualizar usuário existente
                    user.password_hash = password_hash
                    user.is_active = True
                    user.is_admin = is_admin
                    current_app.logger.info(f"Usuário {email} atualizado via SQLAlchemy")
                else:
                    # Criar novo usuário
                    user = User(
                        full_name=full_name,
                        email=email,
                        password_hash=password_hash,
                        is_active=True,
                        is_admin=is_admin
                    )
                    db.session.add(user)
                    current_app.logger.info(f"Usuário {email} criado via SQLAlchemy")
            
            db.session.commit()
            current_app.logger.info("Configuração direta concluída com sucesso")
            
        except Exception as e:
            current_app.logger.error(f"Erro na configuração direta do banco: {e}")
            db.session.rollback()
    
    def validate_auth_request(self):
        """Valida requisições de autenticação"""
        
        # Aplicar apenas para rotas de autenticação
        if not request.endpoint or not request.endpoint.startswith('auth.'):
            return
        
        # Validar requisições de login
        if request.endpoint == 'auth.login' and request.method == 'POST':
            return self._validate_login_request()
    
    def _validate_login_request(self):
        """Valida especificamente requisições de login"""
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Dados de login não fornecidos'
                }), 400
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({
                    'success': False,
                    'message': 'Email e senha são obrigatórios'
                }), 400
            
            # Validar formato do email
            import re
            email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_regex.match(email):
                return jsonify({
                    'success': False,
                    'message': 'Formato de email inválido'
                }), 400
            
            # Log da tentativa de login (sem a senha)
            current_app.logger.info(f"Tentativa de login para: {email}")
            
        except Exception as e:
            current_app.logger.error(f"Erro na validação de login: {e}")
            return jsonify({
                'success': False,
                'message': 'Erro interno do servidor'
            }), 500
    
    @staticmethod
    def require_auth(f):
        """Decorator para rotas que requerem autenticação"""
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implementar lógica de verificação de sessão
            from flask import session
            
            if 'user_id' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Autenticação necessária'
                }), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def require_admin(f):
        """Decorator para rotas que requerem privilégios de admin"""
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            
            if 'user_id' not in session:
                return jsonify({
                    'success': False,
                    'message': 'Autenticação necessária'
                }), 401
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_admin:
                return jsonify({
                    'success': False,
                    'message': 'Privilégios de administrador necessários'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function

# Instância global do middleware
auth_middleware = AuthMiddleware()