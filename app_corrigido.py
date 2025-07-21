#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Definitivo - Sistema Bitget
Versão para deploy no Render.com
"""

import os
import sys
import logging
import sqlite3
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

# Instalar psycopg2 se necessário
try:
    import psycopg2
    logger.info("✅ psycopg2 já está instalado")
except ImportError:
    logger.info("📦 Instalando psycopg2-binary...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
        logger.info("✅ psycopg2-binary instalado com sucesso!")
        import psycopg2
    except Exception as e:
        logger.error(f"❌ Erro ao instalar psycopg2-binary: {e}")

# Criar banco de dados e tabelas
try:
    logger.info("🗄️ Configurando banco de dados...")
    
    # Definir caminho do banco SQLite
    if os.environ.get('RENDER'):
        db_path = '/tmp/site.db'
    else:
        db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
    
    # Garantir que o diretório existe
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Conectar ao banco SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(128),
        is_active BOOLEAN DEFAULT 1,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        operational_balance_usd FLOAT DEFAULT 0.0,
        bitget_api_key_encrypted TEXT,
        bitget_api_secret_encrypted TEXT,
        bitget_passphrase_encrypted TEXT
    )
    ''')
    
    # Criar tabela active_signals
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS active_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol VARCHAR(20) NOT NULL,
        side VARCHAR(10) NOT NULL,
        entry_price FLOAT NOT NULL,
        stop_loss FLOAT,
        take_profit FLOAT,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP,
        user_id INTEGER,
        targets TEXT,
        targets_hit INTEGER DEFAULT 0
    )
    ''')
    
    # Criar tabela user_sessions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Criar tabela trades
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol VARCHAR(20) NOT NULL,
        side VARCHAR(10) NOT NULL,
        quantity FLOAT NOT NULL,
        price FLOAT NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        executed_at TIMESTAMP
    )
    ''')
    
    # Criar usuário demo se não existir
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ('financeiro@lexxusadm.com.br',))
    if cursor.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('FinanceiroDemo2025@')
        
        cursor.execute('''
        INSERT INTO users (full_name, email, password_hash, is_active, is_admin, operational_balance_usd)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Conta Demo Financeiro', 'financeiro@lexxusadm.com.br', password_hash, 1, 0, 600.0))
        
        logger.info("✅ Usuário demo criado com sucesso!")
    
    conn.commit()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    logger.info(f"Tabelas no banco: {tables}")
    
    conn.close()
    logger.info("✅ Banco de dados configurado com sucesso!")
except Exception as e:
    logger.error(f"❌ Erro ao configurar banco de dados: {e}")
    import traceback
    logger.error(traceback.format_exc())

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
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=2592000,  # 30 dias
    )
    
    # Configuração do banco de dados SQLite
    if os.environ.get('RENDER'):
        db_path = '/tmp/site.db'
    else:
        db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Configuração CORS ---
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
    
    # --- Rota Raiz ---
    @app.route('/')
    def home():
        # Verificar se psycopg2 está instalado
        try:
            import psycopg2
            psycopg2_status = "instalado"
        except ImportError:
            psycopg2_status = "não instalado"
        
        # Verificar tabelas do banco
        try:
            import sqlite3
            if os.environ.get('RENDER'):
                db_path = '/tmp/site.db'
            else:
                db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            conn.close()
            
            tabelas_info = f"Tabelas: {', '.join(tables)}"
        except Exception as e:
            tabelas_info = f"Erro ao verificar tabelas: {str(e)}"
        
        return jsonify({
            "message": "BigWhale Backend API", 
            "status": "running", 
            "environment": "Render",
            "psycopg2": psycopg2_status,
            "database": tabelas_info,
            "version": "1.0.0"
        }), 200
    
    # --- Rota de Teste ---
    @app.route('/api/test')
    def test_route():
        return jsonify({"message": "Backend BigWhale funcionando no Render!", "environment": "Render"}), 200
    
    # --- Rota de Health Check ---
    @app.route('/api/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": "Render",
            "message": "Sistema BigWhale funcionando corretamente no Render"
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
            if email == 'financeiro@lexxusadm.com.br' and password == 'FinanceiroDemo2025@':
                return jsonify({
                    "status": "success",
                    "message": "Login realizado com sucesso",
                    "user": {
                        "id": 1,
                        "email": email,
                        "full_name": "Conta Demo Financeiro",
                        "is_admin": False
                    },
                    "token": "demo-token-123456"
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