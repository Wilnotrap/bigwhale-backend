#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask para Deploy no Render
Versão corrigida e simplificada
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Criar e configurar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654')
    app.config['AES_ENCRYPTION_KEY'] = os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    
    # Configurar CORS
    CORS(app, 
         supports_credentials=True,
         origins=[
             "http://localhost:3000",
             "https://bwhale.site",
             "http://bwhale.site"
         ],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    # Configurar banco de dados (PostgreSQL no Render, SQLite local)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        logger.info(f'DATABASE_URL original: {database_url[:50]}...')
        
        # PostgreSQL no Render - corrigir URL se necessário
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            logger.info('URL corrigida de postgres:// para postgresql://')
        
        # Configurações SSL robustas para PostgreSQL no Render
        if 'sslmode' not in database_url:
            separator = '&' if '?' in database_url else '?'
            database_url += f'{separator}sslmode=require'
            logger.info(f'SSL adicionado à URL: sslmode=require')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        logger.info(f'DATABASE_URI final configurada: {database_url[:80]}...')
        logger.info(f'SSL presente na URL: {"sslmode" in database_url}')
        
        # Configurações específicas do engine para Render PostgreSQL (sem connect_args)
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'pool_size': 5,
            'max_overflow': 10
        }
    else:
        # SQLite para desenvolvimento local
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigwhale.db'
        logger.info('Usando SQLite (desenvolvimento)')
        
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300
        }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar SQLAlchemy com tratamento de erro
    from flask_sqlalchemy import SQLAlchemy
    
    logger.info('Iniciando configuração do SQLAlchemy...')
    logger.info(f'SQLALCHEMY_ENGINE_OPTIONS: {app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})}')
    
    try:
        db = SQLAlchemy(app)
        logger.info('SQLAlchemy inicializado com sucesso')
        
        # Testar conexão imediatamente
        with app.app_context():
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            logger.info('Teste de conexão com banco realizado com sucesso')
            
    except Exception as e:
        logger.error(f'Erro ao inicializar SQLAlchemy: {str(e)}')
        logger.error(f'Tipo do erro: {type(e).__name__}')
        
        # Fallback para configuração SSL mais permissiva
        if database_url and 'sslmode=require' in database_url:
            logger.info('Tentando fallback SSL para sslmode=prefer...')
            database_url_fallback = database_url.replace('sslmode=require', 'sslmode=prefer')
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url_fallback
            logger.info(f'DATABASE_URI fallback: {database_url_fallback[:80]}...')
            
            try:
                db = SQLAlchemy(app)
                with app.app_context():
                    from sqlalchemy import text
                    db.session.execute(text('SELECT 1'))
                logger.info('Fallback SSL aplicado com sucesso')
            except Exception as fallback_error:
                logger.error(f'Erro no fallback SSL: {str(fallback_error)}')
                raise fallback_error
        else:
            raise e
    
    # Modelo de usuário simples
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(128), nullable=False)
        full_name = db.Column(db.String(100), nullable=False)
        is_active = db.Column(db.Boolean, default=True)
        is_admin = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def check_password(self, password):
            from werkzeug.security import check_password_hash
            return check_password_hash(self.password_hash, password)
    
    # Modelo de credenciais API
    class APICredentials(db.Model):
        __tablename__ = 'api_credentials'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        api_key = db.Column(db.Text, nullable=False)
        api_secret = db.Column(db.Text, nullable=False)
        passphrase = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin se não existir
        admin = User.query.filter_by(email='admin@bigwhale.com').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(
                email='admin@bigwhale.com',
                password_hash=generate_password_hash('Raikamaster1@'),
                full_name='Admin BigWhale',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info('Usuário admin criado')
    
    # Rotas da API
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Testar conexão com banco
            user_count = User.query.count()
            
            # Detectar tipo de banco
            db_type = 'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            
            return jsonify({
                'status': 'healthy',
                'message': 'BigWhale Backend funcionando no Render',
                'timestamp': datetime.now().isoformat(),
                'database': {
                    'status': 'connected',
                    'type': db_type,
                    'users_count': user_count
                },
                'environment': 'production' if os.environ.get('DATABASE_URL') else 'development',
                'version': '2.0.0'
            }), 200
            
        except Exception as e:
            logger.error(f'Health check error: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': f'Erro no health check: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'database': {
                    'status': 'error',
                    'type': 'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'
                }
            }), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Endpoint de login"""
        try:
            from flask import request
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Email e senha são obrigatórios'}), 400
            
            user = User.query.filter_by(email=data['email']).first()
            
            if user and user.check_password(data['password']):
                return jsonify({
                    'success': True,
                    'message': 'Login realizado com sucesso',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_admin': user.is_admin
                    }
                }), 200
            else:
                return jsonify({'error': 'Credenciais inválidas'}), 401
                
        except Exception as e:
            logger.error(f'Login error: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Endpoint de registro"""
        try:
            from flask import request
            from werkzeug.security import generate_password_hash
            
            data = request.get_json()
            
            if not data or not all(k in data for k in ['email', 'password', 'full_name']):
                return jsonify({'error': 'Dados incompletos'}), 400
            
            # Verificar se usuário já existe
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email já cadastrado'}), 400
            
            # Criar novo usuário
            user = User(
                email=data['email'],
                password_hash=generate_password_hash(data['password']),
                full_name=data['full_name']
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuário criado com sucesso',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name
                }
            }), 201
            
        except Exception as e:
            logger.error(f'Register error: {str(e)}')
            db.session.rollback()
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/credentials/save', methods=['POST'])
    def save_credentials():
        """Salvar credenciais da API"""
        try:
            from flask import request
            
            data = request.get_json()
            
            if not data or not all(k in data for k in ['user_id', 'api_key', 'api_secret', 'passphrase']):
                return jsonify({'error': 'Dados incompletos'}), 400
            
            # Verificar se usuário existe
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            
            # Verificar se já existem credenciais para este usuário
            existing = APICredentials.query.filter_by(user_id=data['user_id']).first()
            
            if existing:
                # Atualizar credenciais existentes
                existing.api_key = data['api_key']
                existing.api_secret = data['api_secret']
                existing.passphrase = data['passphrase']
                existing.updated_at = datetime.utcnow()
            else:
                # Criar novas credenciais
                credentials = APICredentials(
                    user_id=data['user_id'],
                    api_key=data['api_key'],
                    api_secret=data['api_secret'],
                    passphrase=data['passphrase']
                )
                db.session.add(credentials)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Credenciais salvas com sucesso'
            }), 200
            
        except Exception as e:
            logger.error(f'Save credentials error: {str(e)}')
            db.session.rollback()
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/credentials/validate', methods=['POST'])
    def validate_credentials():
        """Validar credenciais da API"""
        try:
            from flask import request
            
            data = request.get_json()
            
            if not data or not data.get('user_id'):
                return jsonify({'error': 'ID do usuário é obrigatório'}), 400
            
            credentials = APICredentials.query.filter_by(user_id=data['user_id']).first()
            
            if credentials:
                return jsonify({
                    'success': True,
                    'has_credentials': True,
                    'message': 'Credenciais encontradas'
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'has_credentials': False,
                    'message': 'Nenhuma credencial encontrada'
                }), 200
                
        except Exception as e:
            logger.error(f'Validate credentials error: {str(e)}')
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/')
    def index():
        """Rota raiz"""
        return jsonify({
            'message': 'BigWhale Backend API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': [
                '/api/health',
                '/api/auth/login',
                '/api/auth/register',
                '/api/credentials/save',
                '/api/credentials/validate'
            ]
        })
    
    return app

# Criar aplicação para o Render
application = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)