#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask - Sistema Bitget
Versão PostgreSQL com asyncpg (sem psycopg2)
"""

import os
import sys
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__)

# Configuração básica
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654')

# Configuração do banco de dados PostgreSQL
database_url = os.environ.get('DATABASE_URL')

if database_url and os.environ.get('RENDER'):
    # PostgreSQL em produção usando asyncpg
    if database_url.startswith('postgres://'):
        # Converter para asyncpg
        database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    elif database_url.startswith('postgresql://'):
        # Converter para asyncpg
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    logger.info("✅ Usando PostgreSQL com asyncpg")
else:
    # SQLite para desenvolvimento local
    db_path = 'site.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    logger.info(f"✅ Usando SQLite local: {db_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração CORS
CORS(app, 
     supports_credentials=True, 
     origins=[
         "http://localhost:3000", 
         "http://localhost:3001", 
         "http://localhost:3002", 
         "https://bwhale.site",
         "http://bwhale.site",
         "https://bigwhale-backend.onrender.com"
     ],
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo de usuário
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Inicializar banco de dados
def init_db():
    try:
        db_type = "PostgreSQL" if os.environ.get('DATABASE_URL') else "SQLite"
        logger.info(f"Iniciando criação do banco de dados {db_type}...")
        
        db.create_all()
        logger.info(f"✅ Tabelas {db_type} criadas com sucesso")
        
        # Criar usuário admin se não existir
        admin_user = User.query.filter_by(email='admin@bigwhale.com').first()
        if not admin_user:
            admin_user = User(
                full_name='Admin BigWhale',
                email='admin@bigwhale.com',
                password_hash=generate_password_hash('Raikamaster1@'),
                is_active=True,
                is_admin=True
            )
            db.session.add(admin_user)
            
            # Criar segundo usuário admin
            admin_user2 = User(
                full_name='Willian Admin',
                email='willian@lexxusadm.com.br',
                password_hash=generate_password_hash('Bigwhale202021@'),
                is_active=True,
                is_admin=True
            )
            db.session.add(admin_user2)
            
            db.session.commit()
            logger.info(f"✅ Usuários admin criados no {db_type}")
        else:
            logger.info(f"✅ Usuários admin já existem no {db_type}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {e}")
        try:
            db.session.rollback()
        except:
            pass

# Inicializar na criação da app
with app.app_context():
    init_db()

# Rotas principais
@app.route('/')
def home():
    db_type = "PostgreSQL" if os.environ.get('DATABASE_URL') else "SQLite"
    return jsonify({
        "message": "🐋 Backend BigWhale Online!",
        "status": "running",
        "environment": "Render" if os.environ.get('RENDER') else "Local",
        "timestamp": datetime.now().isoformat(),
        "version": "7.0.0",
        "database": db_type
    })

@app.route('/api/test')
def test_route():
    db_type = "PostgreSQL" if os.environ.get('DATABASE_URL') else "SQLite"
    return jsonify({
        "message": "🚀 API BigWhale funcionando no Render!",
        "environment": "Render" if os.environ.get('RENDER') else "Local",
        "timestamp": datetime.now().isoformat(),
        "database": db_type,
        "version": "7.0.0",
        "cors_enabled": True
    }), 200

@app.route('/api/health')
def health_check():
    try:
        # Testar conexão com banco
        user_count = User.query.count()
        db_type = "PostgreSQL" if os.environ.get('DATABASE_URL') else "SQLite"
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': {
                'status': 'connected',
                'users_count': user_count,
                'type': db_type
            },
            'environment': 'Render' if os.environ.get('RENDER') else 'Local',
            'version': '7.0.0',
            'message': f'✅ Sistema funcionando com {db_type}'
        }
        
        logger.info(f"Health check OK - {user_count} usuários no {db_type}")
        return jsonify(health_data), 200
        
    except Exception as e:
        logger.error(f"❌ Health check falhou: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'message': '❌ Erro no sistema'
        }), 500

# ROTAS DE AUTENTICAÇÃO
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            # Criar sessão
            session['user_id'] = user.id
            session['user_email'] = user.email
            session.permanent = True
            
            logger.info(f"✅ Login bem-sucedido: {email}")
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
            logger.warning(f"❌ Tentativa de login falhada: {email}")
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/session', methods=['GET'])
def check_session():
    """Verifica se o usuário está logado"""
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_active:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_admin': user.is_admin
                    }
                }), 200
        
        return jsonify({'authenticated': False}), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar sessão: {e}")
        return jsonify({'authenticated': False}), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout do usuário"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout realizado com sucesso'}), 200
    except Exception as e:
        logger.error(f"❌ Erro no logout: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# WEBHOOK STRIPE
@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Webhook do Stripe"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        logger.info(f"✅ Webhook Stripe recebido - Tamanho: {len(payload)} bytes")
        
        # Aqui você implementaria a lógica do webhook
        return jsonify({'received': True, 'status': 'processed'}), 200
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook Stripe: {e}")
        return jsonify({'error': 'Erro no webhook'}), 400

@app.route('/api/users', methods=['GET'])
def list_users():
    try:
        users = User.query.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({
            'users': users_data,
            'count': len(users_data)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar usuários: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Variável para o Render
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Iniciando Backend BigWhale...")
    print(f"🌐 Porta: {port}")
    print(f"🔧 Ambiente: {'Render' if os.environ.get('RENDER') else 'Local'}")
    print("💾 Banco: PostgreSQL (asyncpg)")
    print("📧 Credenciais disponíveis:")
    print("   admin@bigwhale.com / Raikamaster1@")
    print("   willian@lexxusadm.com.br / Bigwhale202021@")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
