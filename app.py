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
        SESSION_COOKIE_SAMESITE='Lax',  # Mudança: None para Lax
        SESSION_COOKIE_SECURE=True,  # Manter True para HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_DOMAIN=None,  # Adicionar esta linha
        PERMANENT_SESSION_LIFETIME=86400,  # 24 horas
        AES_ENCRYPTION_KEY=os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    )
    
    # Configuração do banco de dados SQLite
    # No Render, o sistema de arquivos é efêmero. Usamos /tmp para o DB.
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
    
    # --- Registro de Blueprints (Rotas da API) ---
    from auth.routes import auth_bp
    from api.dashboard import dashboard_bp
    from api.admin import admin_bp
    from api.stripe_webhook import stripe_webhook_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(stripe_webhook_bp, url_prefix='')

    # --- Rota de Teste Simples ---
    @app.route('/api/test')
    def test_route():
        return jsonify({"message": "Backend BigWhale funcionando no Render!"}), 200
    
    @app.route('/api/test-auth')
    def test_auth():
        from flask import session
        return jsonify({
            "message": "Teste de autenticação",
            "session_data": dict(session),
            "has_user_id": 'user_id' in session
        }), 200

    return app

# --- Ponto de Entrada para Gunicorn ---
# O Render usará esta variável 'application' para iniciar o servidor.
application = create_app()

if __name__ == '__main__':
    # Este bloco é para execução local, não será usado pelo Render.
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=True)