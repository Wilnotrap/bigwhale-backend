#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Definitivo - Sistema Bitget
Versão para deploy na Hostinger
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
        PERMANENT_SESSION_LIFETIME=86400,  # 24 horas
        AES_ENCRYPTION_KEY=os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    )
    
    # Configuração do banco de dados SQLite
    # Para Hostinger, usar caminho relativo
    db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Inicialização de Extensões ---
    # Configuração CORS para Hostinger
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
    
    # Inicializar Flask-Session
    from flask_session import Session
    Session(app)
    
    # --- Função para garantir credenciais de admin ---
    def ensure_admin_credentials():
        """Garante que as credenciais de admin estejam corretas na inicialização"""
        try:
            from models.user import User
            from werkzeug.security import generate_password_hash
            
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
            
            db.session.commit()
            app.logger.info("Credenciais de admin configuradas com sucesso")
            
        except Exception as e:
            app.logger.error(f"Erro ao configurar credenciais de admin: {e}")
    
    # --- Registro de Blueprints (Rotas da API) ---
    # Importar blueprints aqui dentro para evitar importação circular
    from auth.routes import auth_bp
    from api.dashboard import dashboard_bp
    from api.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # --- Rota de Teste Simples ---
    @app.route('/api/test')
    def test_route():
        return jsonify({"message": "Backend BigWhale funcionando na Hostinger!", "environment": "Hostinger"}), 200

    # --- Rota de Health Check ---
    @app.route('/api/health')
    def health_check():
        """Endpoint para verificar a saúde da aplicação"""
        try:
            # Verificar conexão com banco
            from models.user import User
            user_count = User.query.count()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'users_count': user_count,
                'environment': 'Hostinger',
                'message': 'Sistema BigWhale funcionando corretamente na Hostinger'
            }), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

    # --- Criação do Banco de Dados ---
    with app.app_context():
        try:
            db.create_all()
            print(f"✅ Tabelas do banco de dados SQLite verificadas/criadas com sucesso!")
            # Garantir credenciais de admin
            ensure_admin_credentials()
        except Exception as e:
            print(f"❌ Erro ao criar tabelas SQLite: {e}")

    return app

# Criar a aplicação para a Hostinger
application = create_app()
app = application  # Alias para compatibilidade

if __name__ == '__main__':
    # Para desenvolvimento local
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Iniciando servidor...")
    print(f"🌐 Porta: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)