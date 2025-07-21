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
import psycopg2
from flask_sqlalchemy import SQLAlchemy

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
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
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        logger.info(f"Usando PostgreSQL: {database_url}")
    else:
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
    db = SQLAlchemy(app)
    try:
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
        with app.app_context():
            db.create_all()
            logger.info("✅ Tabelas do banco de dados criadas com sucesso!")
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

    @app.route('/')
    def home():
        db_info = {}
        try:
            db_info["uri"] = app.config['SQLALCHEMY_DATABASE_URI']
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            db_info["tables"] = tables
            user_count = db.session.query(User).count()
            db_info["users"] = user_count
        except Exception as e:
            db_info["error"] = str(e)
        return jsonify({
            "message": "BigWhale Backend API",
            "status": "running",
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "database": db_info,
            "version": "1.0.0"
        }), 200

    @app.route('/api/test')
    def test_route():
        return jsonify({
            "message": "Backend BigWhale funcionando no Render!",
            "environment": os.environ.get('ENVIRONMENT', 'development')
        }), 200

    @app.route('/api/health')
    def health_check():
        try:
            db.session.execute('SELECT 1')
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "environment": os.environ.get('ENVIRONMENT', 'development'),
                "message": "Sistema BigWhale funcionando corretamente"
            }), 200
        except Exception as e:
            app.logger.error(f"Erro no health check: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({
                "status": "error",
                "message": f"Erro no health check: {str(e)}"
            }), 500

    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            user = db.session.query(User).filter_by(email=email).first()
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
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({
                "status": "error",
                "message": "Erro ao processar login"
            }), 500

    @app.route('/api/auth/session', methods=['GET'])
    def session():
        try:
            user = db.session.query(User).filter_by(email='financeiro@lexxusadm.com.br').first()
            if user:
                return jsonify({
                    "status": "success",
                    "message": "Sessão válida",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "is_admin": user.is_admin
                    }
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Usuário demo não encontrado"
                }), 404
        except Exception as e:
            app.logger.error(f"Erro na sessão: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({
                "status": "error",
                "message": "Erro ao processar sessão"
            }), 500

    @app.route('/api/dashboard/summary', methods=['GET'])
    def summary():
        try:
            user = db.session.query(User).filter_by(email='financeiro@lexxusadm.com.br').first()
            balance = user.operational_balance_usd if user else 0.0
            return jsonify({
                "status": "success",
                "balance": balance,
                "active_signals": db.session.query(ActiveSignal).count(),
                "completed_trades": 0
            }), 200
        except Exception as e:
            app.logger.error(f"Erro no resumo: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({
                "status": "error",
                "message": "Erro ao processar resumo"
            }), 500

    return app

application = create_app()

if __name__ == '__main__':
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