#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Definitivo - Sistema Bitget
Versão para deploy no Render.com
"""

import os
import sys
import logging
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verificar se psycopg2 está instalado
try:
    import psycopg2
    logger.info("✅ psycopg2 já está instalado")
except ImportError:
    logger.error("❌ psycopg2 não está instalado! Tentando instalar...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
        import psycopg2
        logger.info("✅ psycopg2-binary instalado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao instalar psycopg2-binary: {e}")

def create_app(config_name='default'):
    """
    Cria e configura a aplicação Flask (Padrão App Factory).
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # --- Configuração de Logging ---
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/nautilus.log')
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
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=2592000,  # 30 dias
    )
    
    # Configuração do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Render usa postgresql:// em vez de postgres://
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        logger.info(f"Usando PostgreSQL: {database_url}")
    else:
        # Fallback para SQLite
        if os.environ.get('RENDER'):
            db_path = '/tmp/site.db'
        else:
            db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        logger.info(f"Usando SQLite: {db_path}")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Configuração CORS ---
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    if cors_origins != '*':
        cors_origins = cors_origins.split(',')
    
    CORS(app, 
         supports_credentials=True, 
         origins=cors_origins,
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # --- Inicialização do Banco de Dados ---
    try:
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy(app)
        
        # Definir modelo User
        class User(db.Model):
            __tablename__ = 'users'
            
            id = db.Column(db.Integer, primary_key=True)
            full_name = db.Column(db.String(100), nullable=False)
            email = db.Column(db.String(120), unique=True, nullable=False)
            password_hash = db.Column(db.String(128))
            is_active = db.Column(db.Boolean, default=True)
            is_admin = db.Column(db.Boolean, default=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            operational_balance_usd = db.Column(db.Float, default=0.0)
            
            def check_password(self, password):
                from werkzeug.security import check_password_hash
                return check_password_hash(self.password_hash, password)
        
        # Definir modelo ActiveSignal
        class ActiveSignal(db.Model):
            __tablename__ = 'active_signals'
            
            id = db.Column(db.Integer, primary_key=True)
            symbol = db.Column(db.String(20), nullable=False)
            side = db.Column(db.String(10), nullable=False)
            entry_price = db.Column(db.Float, nullable=False)
            stop_loss = db.Column(db.Float, nullable=True)
            take_profit = db.Column(db.Float, nullable=True)
            status = db.Column(db.String(20), default='active')
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            closed_at = db.Column(db.DateTime, nullable=True)
            user_id = db.Column(db.Integer, nullable=True)
            
        # Criar tabelas
        with app.app_context():
            db.create_all()
            logger.info("✅ Tabelas do banco de dados criadas com sucesso!")
            
            # Criar usuário demo se não existir
            demo_user = User.query.filter_by(email='financeiro@lexxusadm.com.br').first()
            if not demo_user:
                from werkzeug.security import generate_password_hash
                demo_user = User(
                    full_name='Conta Demo Financeiro',
                    email='financeiro@lexxusadm.com.br',
                    password_hash=generate_password_hash('FinanceiroDemo2025@'),
                    is_active=True,
                    is_admin=False,
                    operational_balance_usd=600.0
                )
                db.session.add(demo_user)
                db.session.commit()
                logger.info("✅ Usuário demo criado com sucesso!")
    
    except Exception as e:
        logger.error(f"❌ Erro ao configurar banco de dados: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # --- Rota Raiz ---
    @app.route('/')
    def home():
        # Verificar se psycopg2 está instalado
        try:
            import psycopg2
            psycopg2_status = "instalado"
        except ImportError:
            psycopg2_status = "não instalado"
        
        # Verificar banco de dados
        db_info = {}
        try:
            db_info["uri"] = app.config['SQLALCHEMY_DATABASE_URI']
            
            # Verificar tabelas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            db_info["tables"] = tables
            
            # Verificar usuários
            user_count = User.query.count()
            db_info["users"] = user_count
            
        except Exception as e:
            db_info["error"] = str(e)
        
        return jsonify({
            "message": "BigWhale Backend API", 
            "status": "running", 
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "psycopg2": psycopg2_status,
            "database": db_info,
            "version": "1.0.0"
        }), 200
    
    # --- Rota de Teste ---
    @app.route('/api/test')
    def test_route():
        return jsonify({
            "message": "Backend BigWhale funcionando no Render!",
            "environment": os.environ.get('ENVIRONMENT', 'development')
        }), 200
    
    # --- Rota de Health Check ---
    @app.route('/api/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "message": "Sistema BigWhale funcionando corretamente"
        }), 200
    
    # --- Rota de Login ---
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        if request.method == 'OPTIONS':
            # Responder a requisições OPTIONS para CORS
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        # Processar login
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            # Verificar credenciais
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                return jsonify({
                    "status": "success",
                    "message": "Login realizado com sucesso",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "is_admin": user.is_admin
                    },
                    "token": f"demo-token-{user.id}"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Credenciais inválidas"
                }), 401
        except Exception as e:
            app.logger.error(f"Erro no login: {e}")
            return jsonify({
                "status": "error",
                "message": "Erro ao processar login"
            }), 500
    
    # --- Rota de Sessão ---
    @app.route('/api/auth/session', methods=['GET'])
    def session():
        # Em uma implementação real, verificaríamos o token
        # Aqui, apenas retornamos o usuário demo
        return jsonify({
            "status": "success",
            "message": "Sessão válida",
            "user": {
                "id": 1,
                "email": "financeiro@lexxusadm.com.br",
                "full_name": "Conta Demo Financeiro",
                "is_admin": False
            }
        }), 200
    
    # --- Rota de Resumo ---
    @app.route('/api/dashboard/summary', methods=['GET'])
    def summary():
        return jsonify({
            "status": "success",
            "balance": 600.0,
            "active_signals": 0,
            "completed_trades": 0
        }), 200
    
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
    print("   financeiro@lexxusadm.com.br / FinanceiroDemo2025@")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )