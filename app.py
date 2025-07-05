#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Definitivo - Sistema Bitget
Versão para deploy no Render.com
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import db

import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def create_admin_users(app):
    """
    Cria usuários admin se não existirem
    """
    try:
        from models.user import User
        
        # Verificar se já existem usuários admin
        admin_exists = User.query.filter_by(is_admin=True).first()
        
        if not admin_exists:
            admin_users = [
                {
                    'full_name': 'Admin Principal',
                    'email': 'admin@bwhale.site',
                    'password': 'Admin123!@#',
                    'is_admin': True,
                    'has_paid': True,
                    'subscription_status': 'active',
                    'payment_status': 'paid'
                },
                {
                    'full_name': 'Admin Teste',
                    'email': 'teste@bwhale.site',
                    'password': 'Teste123!@#',
                    'is_admin': True,
                    'has_paid': True,
                    'subscription_status': 'active',
                    'payment_status': 'paid'
                },
                {
                    'full_name': 'Usuario Demo',
                    'email': 'demo@bwhale.site',
                    'password': 'Demo123!@#',
                    'is_admin': False,
                    'has_paid': True,
                    'subscription_status': 'active',
                    'payment_status': 'paid'
                }
            ]
            
            for user_data in admin_users:
                user = User(
                    full_name=user_data['full_name'],
                    email=user_data['email'],
                    is_admin=user_data['is_admin'],
                    has_paid=user_data['has_paid'],
                    subscription_status=user_data['subscription_status'],
                    payment_status=user_data['payment_status']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
            
            db.session.commit()
            app.logger.info('✅ Usuários admin criados com sucesso!')
            
            # Verificar criação
            total_users = User.query.count()
            admin_count = User.query.filter_by(is_admin=True).count()
            app.logger.info(f'✅ Total de usuários: {total_users}')
            app.logger.info(f'✅ Usuários admin: {admin_count}')
            
        else:
            app.logger.info('ℹ️ Usuários admin já existem no banco de dados')
            
    except Exception as e:
        app.logger.error(f'❌ Erro ao criar usuários admin: {str(e)}')
        db.session.rollback()

def create_app(config_name='default'):
    """
    Cria e configura a aplicação Flask (Padrão App Factory).
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # --- Configuração de Logging ---
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nautilus.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Nautilus startup')
    
    # --- Configuração da Aplicação ---
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'),
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_DOMAIN=None,
        PERMANENT_SESSION_LIFETIME=86400,
        AES_ENCRYPTION_KEY=os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    )
    
    # Configuração do banco de dados SQLite
    db_path = os.path.join('/tmp', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Inicialização de Extensões ---
    CORS(app, 
         supports_credentials=True, 
         origins=[
             "http://localhost:3000", 
             "http://localhost:3001", 
             "https://bwhale.site", 
             "http://bwhale.site",
             "https://www.bwhale.site",
             "http://www.bwhale.site"
         ],
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         expose_headers=["Set-Cookie"])
    
    db.init_app(app)
    
    # *** CRÍTICO: Importar TODOS os models ANTES de criar tabelas ***
    with app.app_context():
        try:
            # IMPORTAR TODOS OS MODELS PRIMEIRO
            from models.user import User
            from models.trade import Trade
            from models.session import UserSession
            
            app.logger.info('✅ Models importados com sucesso!')
            
            # AGORA criar as tabelas
            db.create_all()
            app.logger.info('✅ Tabelas do banco de dados criadas com sucesso!')
            
            # Criar usuários admin
            create_admin_users(app)
            
        except Exception as e:
            app.logger.error(f'❌ Erro ao inicializar banco: {str(e)}')
            import traceback
            app.logger.error(f'❌ Traceback: {traceback.format_exc()}')
    
    # --- Registro de Blueprints (Rotas da API) ---
    try:
        from auth.routes import auth_bp
        from api.dashboard import dashboard_bp
        from api.admin import admin_bp
        from api.stripe_webhook import stripe_webhook_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(stripe_webhook_bp, url_prefix='')
        
        app.logger.info('✅ Blueprints registrados com sucesso!')
    except Exception as e:
        app.logger.error(f'❌ Erro ao registrar blueprints: {str(e)}')

    # --- Rotas de Teste e Debug ---
    @app.route('/api/test')
    def test_route():
        return jsonify({"message": "Backend BigWhale funcionando no Render!"}), 200
    
    @app.route('/api/test-auth')
    def test_auth():
        from flask import session
        return jsonify({
            "message": "Teste de autenticação",
            "session_data": dict(session),
            "has_user_id": 'user_id' in session,
            "backend_url": "https://bigwhale-backend.onrender.com"
        }), 200
    
    @app.route('/api/debug')
    def debug_route():
        try:
            from models.user import User
            user_count = User.query.count()
            admin_count = User.query.filter_by(is_admin=True).count()
            return jsonify({
                "status": "OK",
                "database_connected": True,
                "user_count": user_count,
                "admin_count": admin_count,
                "tables_created": True
            }), 200
        except Exception as e:
            return jsonify({
                "status": "ERROR",
                "database_connected": False,
                "error": str(e)
            }), 500
    
    # --- Error Handlers ---
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'❌ Erro 500: {str(error)}')
        return jsonify({
            "error": "Internal Server Error",
            "message": "Erro interno do servidor. Verifique os logs."
        }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "Endpoint não encontrado"
        }), 404

    return app

# --- Ponto de Entrada para Gunicorn ---
application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=True)