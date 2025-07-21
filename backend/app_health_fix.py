#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Definitivo - Sistema Bitget
Versão para deploy no Render.com
FORÇADO PARA SQLITE LOCAL
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import db

import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta, datetime

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
    
    # Configuração do banco de dados - FORÇADO PARA SQLITE
    db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.logger.info("FORÇADO: Usando SQLite local (ignorando DATABASE_URL)")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Inicialização de Extensões ---
    # Configuração CORS global para desenvolvimento e produção
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
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    db.init_app(app)

    # Garanta que as tabelas do banco de dados sejam criadas
    # Isso é crucial para o SQLite criar o arquivo .db no diretório correto (/tmp no Render)
    with app.app_context():
        db.create_all()
        app.logger.info("Tabelas do banco de dados garantidas na inicialização.")
    
    # Configurar Flask-Session com configurações mais simples
    try:
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
        from flask_session import Session
        Session(app)
        app.logger.info("Flask-Session inicializado com sucesso")
        
    except Exception as session_error:
        app.logger.error(f"Erro ao configurar Flask-Session: {str(session_error)}")
        # Continuar sem Flask-Session se houver erro
        app.config['SESSION_TYPE'] = 'null'
    
    # --- Função para garantir credenciais de admin ---
    def ensure_admin_credentials():
        """Garante que as credenciais de admin estejam corretas na inicialização"""
        try:
            # Importar aqui para evitar problemas de importação circular
            from models.user import User
            from werkzeug.security import generate_password_hash
            
            # Verificar se a tabela users existe antes de tentar acessá-la
            try:
                # Teste rápido para ver se a tabela existe
                User.query.first()
            except Exception as table_error:
                app.logger.warning(f"Tabela users não encontrada, criando: {table_error}")
                # Forçar criação da tabela se não existir
                db.create_all()
                app.logger.info("Tabelas recriadas após erro")
            
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
                try:
                    user = User.query.filter_by(email=admin_data['email']).first()
                    
                    if user:
                        # Atualizar senha e status de admin se necessário
                        if not user.check_password(admin_data['password']):
                            user.password_hash = generate_password_hash(admin_data['password'])
                            user.is_active = True
                            app.logger.info(f"Credenciais atualizadas para {admin_data['email']}")
                        
                        # Garantir que o status de admin esteja correto
                        if user.is_admin != admin_data['is_admin']:
                            user.is_admin = admin_data['is_admin']
                            app.logger.info(f"Status de admin atualizado para {admin_data['email']}: {admin_data['is_admin']}")
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
                        app.logger.info(f"Usuário {admin_data['email']} criado")
                except Exception as user_error:
                    app.logger.error(f"Erro ao processar usuário {admin_data['email']}: {user_error}")
                    continue
            
            try:
                db.session.commit()
                app.logger.info("Credenciais de admin configuradas com sucesso")
            except Exception as commit_error:
                db.session.rollback()
                app.logger.error(f"Erro ao salvar credenciais: {commit_error}")
            
        except Exception as e:
            app.logger.error(f"Erro ao configurar credenciais de admin: {e}")
            # Não interromper a inicialização por causa disso
    
    # --- Registro de Blueprints (Rotas da API) ---
    # Importar blueprints aqui dentro para evitar importação circular
    from auth.routes import auth_bp
    from api.dashboard import dashboard_bp
    from api.admin import admin_bp
    from api.stripe_webhook import stripe_webhook_bp
    from services.secure_api_service_corrigido import SecureAPIService

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(stripe_webhook_bp, url_prefix='/api')

    # Inicializar APIPersistence e CredentialMonitor
    from utils.api_persistence import APIPersistence
    from services.credential_monitor import CredentialMonitor
    
    # Crie a instância de APIPersistence (auto-detecta caminho do banco)
    api_persistence_instance = APIPersistence()
    
    # Crie a instância de CredentialMonitor, passando a APIPersistence
    credential_monitor_instance = CredentialMonitor(app, api_persistence_instance)
    
    # Inicialize SecureAPIService UMA VEZ APENAS
    secure_api_service = SecureAPIService(app)

    # --- Rota de Teste Simples ---
    @app.route('/api/test')
    def test_route():
        return jsonify({"message": "Backend BigWhale funcionando no Render!", "environment": "Render"}), 200

    # --- Rota para Inicializar Banco de Dados ---
    @app.route('/api/init-database')
    def init_database():
        """Endpoint para forçar a inicialização do banco de dados"""
        try:
            app.logger.info("=== INICIALIZAÇÃO FORÇADA DO BANCO ===")
            
            # Forçar criação das tabelas
            db.create_all()
            app.logger.info("Tabelas criadas com sucesso")
            
            # Garantir credenciais de admin
            ensure_admin_credentials()
            
            # Verificar se funcionou
            from models.user import User
            user_count = User.query.count()
            
            return jsonify({
                "success": True,
                "message": "Banco de dados inicializado com sucesso",
                "user_count": user_count,
                "database_uri": app.config['SQLALCHEMY_DATABASE_URI']
            }), 200
            
        except Exception as e:
            app.logger.error(f"Erro ao inicializar banco: {e}")
            return jsonify({
                "success": False,
                "message": f"Erro ao inicializar banco: {str(e)}"
            }), 500

    # --- Rota de Health Check ---
    @app.route('/api/health')
    def health_check():
        """Endpoint de health check para monitoramento"""
        try:
            # Teste básico do banco de dados
            db.session.execute('SELECT 1')
            
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": "connected",
                "environment": "development (SQLite forced)"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "environment": "development (SQLite forced)"
            }), 500

    # Garantir credenciais de admin na inicialização
    with app.app_context():
        ensure_admin_credentials()
    
    return app

# Criação da aplicação
application = create_app()

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5000) 