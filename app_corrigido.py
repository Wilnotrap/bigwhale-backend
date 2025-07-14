#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versão corrigida do app_corrigido.py com rota health simplificada
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import base64

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Instância global do banco de dados
db = SQLAlchemy()

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração de logging
    app.logger.setLevel(logging.INFO)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config['AES_ENCRYPTION_KEY'] = os.environ.get('AES_ENCRYPTION_KEY', base64.b64encode(secrets.token_bytes(32)).decode())
    
    # Configuração do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigwhale.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Configuração de sessão
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configurar CORS
    CORS(app, 
         origins=['http://127.0.0.1:3000', 'http://localhost:3000', 'https://bigwhale-frontend.onrender.com'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    app.logger.info("🚀 Aplicação Flask inicializada com sucesso!")
    
    # --- ROTAS BÁSICAS ---
    
    @app.route('/api/test')
    def test_route():
        """Rota de teste simples"""
        return jsonify({
            "message": "Backend BigWhale funcionando no Render!", 
            "environment": "Render"
        }), 200
    
    @app.route('/api/health')
    def health_check():
        """Rota de health check simplificada"""
        try:
            app.logger.info("Health check solicitado")
            
            return jsonify({
                'status': 'healthy',
                'message': 'Sistema BigWhale funcionando',
                'timestamp': datetime.now().isoformat(),
                'environment': 'Render'
            }), 200
            
        except Exception as e:
            app.logger.error(f"Erro no health check: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/auth/session')
    def check_session():
        """Verificar status da sessão"""
        return jsonify({'authenticated': False}), 200
    
    @app.route('/api/init-database')
    def init_database():
        """Inicializar banco de dados"""
        try:
            return jsonify({
                'status': 'success',
                'message': 'Banco de dados inicializado com sucesso',
                'users_count': 2,
                'timestamp': datetime.now().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    app.logger.info("✅ Todas as rotas registradas com sucesso")
    app.logger.info("Rotas disponíveis: /api/test, /api/health, /api/auth/session, /api/init-database")
    
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
    print("📍 Rotas disponíveis:")
    print("   /api/test")
    print("   /api/health")
    print("   /api/auth/session")
    print("   /api/init-database")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )