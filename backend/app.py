#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Definitivo - Sistema Bitget
Versão para deploy no Render.com
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from database import db
from flask_migrate import Migrate
from sqlalchemy import text

import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta, datetime

# Importar blueprints e serviços
from auth.routes import auth_bp
from api.dashboard import dashboard_bp
from api.admin import admin_bp
from api.stripe_webhook import stripe_webhook_bp
from api import api_credentials_bp
from services.secure_api_service_corrigido import SecureAPIService # Adicionar esta linha
from middleware.auth_middleware import AuthMiddleware
from auth.login import ensure_admin_credentials
from models.invite_code import initialize_invite_codes # Importar a função de inicialização de convites

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def create_app(config_name='default'):
    """
    Cria e configura a aplicação Flask (Padrão App Factory).
    """
    # Adiciona o diretório 'backend' ao path para resolver importações relativas
    import sys
    sys.path.append(os.path.dirname(__file__))

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
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True,  # True para produção com HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=2592000,  # 30 dias (30 * 24 * 60 * 60 segundos)
        AES_ENCRYPTION_KEY=os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    )
    
    # --- Configuração do Banco de Dados Flexível (PostgreSQL ou SQLite) ---
    database_url = os.environ.get('DATABASE_URL')

    if database_url and database_url.startswith('postgres'):
        # Em produção (Render), usar a DATABASE_URL (PostgreSQL)
        # A URL do Render pode vir como 'postgres://' e o SQLAlchemy espera 'postgresql://'
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://', 1)
        app.logger.info("Conectando ao banco de dados PostgreSQL no Render.")
    else:
        # Em desenvolvimento local, usar SQLite
        instance_path = app.instance_path
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            app.logger.info(f"Diretório de instância criado em: {instance_path}")

        db_path = os.path.join(instance_path, 'site.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.logger.info(f"Conectando ao banco de dados SQLite em: {db_path}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Inicialização de Extensões ---
    # Configuração CORS robusta para produção
    CORS(app, 
         supports_credentials=True, 
         origins=[
             "http://localhost:3000", 
             "http://localhost:3001", 
             "http://localhost:3002", 
             "http://127.0.0.1:3000", 
             "http://127.0.0.1:3001", 
             "http://127.0.0.1:3002",
             "https://bwhale.site",
             "http://bwhale.site"
         ],
         allow_headers=[
             "Content-Type", 
             "Authorization", 
             "Access-Control-Allow-Credentials",
             "Access-Control-Allow-Origin",
             "X-Requested-With",
             "Accept"
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"])
    db.init_app(app)

    # Inicializar o Flask-Migrate
    migrate = Migrate(app, db)

    # Inicializar o serviço de API segura
    secure_api_service = SecureAPIService(app)

    # Garanta que as tabelas do banco de dados sejam criadas e dados iniciais configurados
    with app.app_context():
        db.create_all()
        app.logger.info("Tabelas do banco de dados garantidas na inicialização.")
        ensure_admin_credentials() # Garante credenciais de admin
        initialize_invite_codes(app) # Inicializa os códigos de convite

    # Configurar Flask-Session com configurações mais simples
    try:
        from flask_session import Session
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_PERMANENT'] = True
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_KEY_PREFIX'] = 'bigwhale:'
        app.config['SESSION_FILE_DIR'] = os.path.join(app.instance_path, 'flask_session')
        app.config['SESSION_FILE_THRESHOLD'] = 500
        app.config['SESSION_FILE_MODE'] = 384
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30) # 30 dias
        
        # Garantir que o diretório de sessão existe
        session_dir = app.config['SESSION_FILE_DIR']
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
            app.logger.info(f"Diretório de sessão criado: {session_dir}")
        
        # Inicializar Flask-Session
        Session(app)
        app.logger.info("Flask-Session inicializado com sucesso")
        
    except Exception as session_error:
        app.logger.error(f"Erro ao configurar Flask-Session: {str(session_error)}")
        # Continuar sem Flask-Session se houver erro
        app.config['SESSION_TYPE'] = 'null'

    # --- Registro de Blueprints (Rotas da API) ---
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(stripe_webhook_bp, url_prefix='/api')
    app.register_blueprint(api_credentials_bp, url_prefix='/api')

    # Middleware de autenticação
    AuthMiddleware(app)

    # --- Handler global para OPTIONS (preflight requests) ---
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,Access-Control-Allow-Credentials,X-Requested-With,Accept")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response

    # --- Rota de Teste Simples ---
    @app.route('/api/test')
    def test_route():
        return jsonify({"message": "Backend BigWhale funcionando no Render!", "environment": "Render"}), 200

    # --- Rota de Health Check ---
    @app.route('/api/health')
    def health_check():
        """Endpoint para verificar a saúde da aplicação"""
        try:
            # Testar conexão com banco de dados
            db.session.execute(text('SELECT 1'))
            
            return jsonify({
                'status': 'healthy',
                'message': 'Aplicação funcionando corretamente',
                'timestamp': datetime.now().isoformat(),
                'database': 'connected'
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'message': f'Erro na aplicação: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'database': 'disconnected'
            }), 500

    # --- Rota para Inicializar Banco de Dados (redundante, mas pode ser útil para debug) ---
    @app.route('/api/init-database')
    def init_database():
        try:
            app.logger.info("=== INICIALIZAÇÃO FORÇADA DO BANCO ===")
            
            db.create_all()
            app.logger.info("Tabelas criadas com sucesso")
            
            ensure_admin_credentials()
            initialize_invite_codes(app)
            
            from models.user import User
            user_count = User.query.count()
            
            return jsonify({
                'status': 'success',
                'message': 'Banco de dados inicializado com sucesso',
                'users_count': user_count,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            app.logger.error(f"Erro ao inicializar banco de dados: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return app

# Criar a aplicação para o Render
application = create_app()

if __name__ == '__main__':
    # Para desenvolvimento local
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Iniciando servidor...")
    print(f"🌐 Porta: {port}")
    print("🔧 Ambiente: Desenvolvimento")
    print("📧 Credenciais disponíveis:")
    print("   admin@bigwhale.com / Raikamaster1@")
    print("   willian@lexxusadm.com.br / Bigwhale202021@ (ADMIN)")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )