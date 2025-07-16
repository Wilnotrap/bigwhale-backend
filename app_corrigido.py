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
    
    # Configuração do banco de dados
    # Usar PostgreSQL se DATABASE_URL estiver disponível, senão SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # PostgreSQL no Render
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.logger.info("Usando PostgreSQL do Render")
    else:
        # SQLite para desenvolvimento local
        if os.environ.get('RENDER'):
            db_path = '/tmp/site.db'
        else:
            db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.logger.info("Usando SQLite local")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Inicialização de Extensões ---
    # Configuração CORS mais permissiva para produção, incluindo o domínio da Hostinger
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
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
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

    # Inicializar SecureAPIService e registrar suas rotas
    # Inicializar SecureAPIService (versão corrigida)
    secure_api_service = SecureAPIService(app)
    from utils.api_persistence import APIPersistence
    from services.credential_monitor import CredentialMonitor
    
    # Crie a instância de APIPersistence com o caminho correto
    api_persistence_instance = APIPersistence(api_persistence_db_path)
    
    # Crie a instância de CredentialMonitor, passando a APIPersistence
    credential_monitor_instance = CredentialMonitor(app, api_persistence_instance)
    
    # Inicialize SecureAPIService, passando a CredentialMonitor
    secure_api_service = SecureAPIService(app, credential_monitor_instance)

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
                'status': 'success',
                'message': 'Banco de dados inicializado com sucesso',
                'users_count': user_count,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            app.logger.error(f"Erro na inicialização: {str(e)}")
            import traceback
            app.logger.error(f"Traceback: {traceback.format_exc()}")
            
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    # --- Rota de Health Check ---
    @app.route('/api/health')
    def health_check():
        """Endpoint para verificar a saúde da aplicação"""
        try:
            app.logger.info("=== HEALTH CHECK INICIADO ===")
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'environment': 'Render',
                'message': 'Sistema BigWhale funcionando corretamente no Render'
            }
            
            # Verificar conexão com banco
            try:
                from models.user import User
                user_count = User.query.count()
                health_data['database'] = 'connected'
                health_data['users_count'] = user_count
                app.logger.info(f"Banco de dados conectado - {user_count} usuários")
            except Exception as db_error:
                app.logger.error(f"Erro no banco de dados: {str(db_error)}")
                health_data['database'] = 'error'
                health_data['database_error'] = str(db_error)
            
            # Verificar configurações críticas
            try:
                secret_key_ok = bool(app.config.get('SECRET_KEY'))
                aes_key_ok = bool(app.config.get('AES_ENCRYPTION_KEY'))
                
                health_data['config'] = {
                    'secret_key': secret_key_ok,
                    'aes_encryption_key': aes_key_ok
                }
                
                app.logger.info(f"Configurações - Secret Key: {secret_key_ok}, AES Key: {aes_key_ok}")
            except Exception as config_error:
                app.logger.error(f"Erro nas configurações: {str(config_error)}")
                health_data['config_error'] = str(config_error)
            
            # Verificar importações críticas
            try:
                from utils.security import encrypt_api_key, decrypt_api_key
                from models.session import UserSession
                health_data['imports'] = 'ok'
                app.logger.info("Importações críticas verificadas")
            except Exception as import_error:
                app.logger.error(f"Erro nas importações: {str(import_error)}")
                health_data['imports'] = 'error'
                health_data['import_error'] = str(import_error)
            
            app.logger.info("=== HEALTH CHECK CONCLUÍDO ===")
            return jsonify(health_data), 200
            
        except Exception as e:
            app.logger.error(f"=== HEALTH CHECK FALHOU ===")
            app.logger.error(f"Erro: {str(e)}")
            
            import traceback
            app.logger.error(f"Traceback: {traceback.format_exc()}")
            
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    # --- Criação do Banco de Dados ---
    with app.app_context():
        try:
            app.logger.info("=== INICIANDO CRIAÇÃO DO BANCO DE DADOS ===")
            
            # Garantir que o diretório do banco existe
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            app.logger.info(f"URI do banco: {db_uri}")
            
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    app.logger.info(f"Diretório do banco criado: {db_dir}")
                app.logger.info(f"Caminho do banco SQLite: {db_path}")
            
            # Importar todos os modelos antes de criar as tabelas
            try:
                from models.user import User
                from models.session import UserSession
                from models.trade import Trade
                app.logger.info("Modelos importados com sucesso")
            except Exception as import_error:
                app.logger.error(f"Erro ao importar modelos: {import_error}")
            
            # Criar todas as tabelas
            db.create_all()
            app.logger.info("✅ Tabelas do banco de dados SQLite verificadas/criadas com sucesso!")
            print(f"✅ Tabelas do banco de dados SQLite verificadas/criadas com sucesso!")
            
            # Verificar se as tabelas foram realmente criadas
            try:
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                app.logger.info(f"Tabelas encontradas no banco: {tables}")
                
                if 'users' in tables:
                    app.logger.info("✅ Tabela 'users' confirmada")
                else:
                    app.logger.warning("⚠️ Tabela 'users' não encontrada")
                    
            except Exception as inspect_error:
                app.logger.error(f"Erro ao inspecionar banco: {inspect_error}")
            
            # Aguardar um pouco para garantir que as tabelas foram criadas
            import time
            time.sleep(0.5)
            
            # Garantir credenciais de admin
            app.logger.info("Iniciando configuração de credenciais de admin...")
            ensure_admin_credentials()
            
            app.logger.info("=== CRIAÇÃO DO BANCO DE DADOS CONCLUÍDA ===")
            
        except Exception as e:
            app.logger.error(f"❌ Erro ao criar tabelas SQLite: {e}")
            print(f"❌ Erro ao criar tabelas SQLite: {e}")
            import traceback
            app.logger.error(f"Traceback: {traceback.format_exc()}")
            # Continuar mesmo com erro para que o servidor rode
            pass

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