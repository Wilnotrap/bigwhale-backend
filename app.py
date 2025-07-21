#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação principal do BigWhale Backend
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta
from database import db

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração padrão
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_TYPE='filesystem',
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
    )
    
    # Configurar banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Render usa postgresql:// em vez de postgres://
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        logger.info("Usando PostgreSQL para produção")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///' + os.path.join(app.instance_path, 'site.db')
        logger.info("Usando SQLite para desenvolvimento")
    
    # Garantir que o diretório de instância existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configurar CORS
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    if cors_origins != '*':
        cors_origins = cors_origins.split(',')
    CORS(app, 
         origins=cors_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Importar e registrar blueprints
    from api.auth import auth_bp
    from api.demo_trading import demo_trading_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(demo_trading_bp, url_prefix='/api')
    
    # Rota de teste
    @app.route('/api/health')
    def health_check():
        logger.info("Health check endpoint accessed")
        return jsonify({'status': 'ok', 'message': 'BigWhale Backend is running'})
    
    # Criar tabelas do banco de dados
    with app.app_context():
        try:
            db.create_all()
            logger.info("Tabelas do banco de dados criadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)