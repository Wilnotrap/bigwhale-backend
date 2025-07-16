#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Otimizado para Render
Sistema BigWhale - Versão Deploy
"""

import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import logging
import jwt
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__)

# Configuração básica
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Configuração do banco de dados
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # PostgreSQL no Render
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    logger.info("✅ Usando PostgreSQL no Render")
else:
    # SQLite para desenvolvimento
    if os.environ.get('RENDER'):
        db_path = '/tmp/site.db'
    else:
        db_path = 'site.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    logger.info("✅ Usando SQLite local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração CORS
CORS(app, 
     supports_credentials=True, 
     origins=[
         "http://localhost:3000", 
         "http://localhost:3001", 
         "http://localhost:3002", 
         "https://bwhale.site",
         "http://bwhale.site"
     ],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# ================================
# MODELOS DO BANCO DE DADOS
# ================================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Campos para API Bitget
    api_key = db.Column(db.Text, nullable=True)
    api_secret = db.Column(db.Text, nullable=True)
    api_passphrase = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # buy/sell
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('trades', lazy=True))

# ================================
# UTILITÁRIOS DE AUTENTICAÇÃO
# ================================

def require_login(f):
    """Decorator para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        
        # Renovar sessão
        session.permanent = True
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator para verificar se o usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Acesso negado - Admin necessário'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ================================
# INICIALIZAÇÃO DO BANCO
# ================================

def init_database():
    """Inicializar banco de dados e usuários padrão"""
    try:
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            logger.info("✅ Tabelas criadas com sucesso")
            
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
                db.session.commit()
                logger.info("✅ Usuário admin criado: admin@bigwhale.com")
            
            # Criar usuário Willian se não existir
            willian_user = User.query.filter_by(email='willian@lexxusadm.com.br').first()
            if not willian_user:
                willian_user = User(
                    full_name='Willian Lexxus',
                    email='willian@lexxusadm.com.br',
                    password_hash=generate_password_hash('Bigwhale202021@'),
                    is_active=True,
                    is_admin=True
                )
                db.session.add(willian_user)
                db.session.commit()
                logger.info("✅ Usuário Willian criado: willian@lexxusadm.com.br")
                
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {e}")

# ================================
# ROTAS PRINCIPAIS
# ================================

@app.route('/')
def home():
    """Página inicial da API"""
    return jsonify({
        "message": "🚀 Backend BigWhale Online!",
        "status": "healthy",
        "environment": "Render" if os.environ.get('RENDER') else "Local",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/api/health",
            "login": "/api/auth/login",
            "register": "/api/auth/register",
            "profile": "/api/profile"
        }
    })

@app.route('/api/health')
def health_check():
    """Health check para o Render"""
    try:
        # Testar conexão com banco
        user_count = User.query.count()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": "Render" if os.environ.get('RENDER') else "Local",
            "database": "connected",
            "users_count": user_count,
            "message": "Sistema BigWhale funcionando corretamente"
        }), 200
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/test')
def test_route():
    """Rota de teste"""
    return jsonify({
        "message": "✅ API funcionando perfeitamente!",
        "environment": "Render" if os.environ.get('RENDER') else "Local",
        "timestamp": datetime.now().isoformat()
    })

# ================================
# ROTAS DE AUTENTICAÇÃO
# ================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Criar sessão
        session.permanent = True
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['is_admin'] = user.is_admin
        
        logger.info(f"✅ Login realizado: {user.email}")
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Cadastro de usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([full_name, email, password]):
            return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Criar usuário
        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            is_active=True,
            is_admin=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"✅ Usuário registrado: {email}")
        
        return jsonify({
            'message': 'Usuário cadastrado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Erro no registro: {e}")
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_login
def logout():
    """Logout do usuário"""
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

# ================================
# ROTAS DE PERFIL
# ================================

@app.route('/api/profile')
@require_login
def get_profile():
    """Obter perfil do usuário"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'has_api_credentials': bool(user.api_key and user.api_secret)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar perfil: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/save-credentials', methods=['POST'])
@require_login
def save_credentials():
    """Salvar credenciais da API Bitget"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        api_key = data.get('apiKey')
        api_secret = data.get('apiSecret')
        passphrase = data.get('passphrase')
        
        if not all([api_key, api_secret, passphrase]):
            return jsonify({'error': 'Todas as credenciais são obrigatórias'}), 400
        
        # Buscar usuário
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Salvar credenciais (em produção, criptografar)
        user.api_key = api_key
        user.api_secret = api_secret
        user.api_passphrase = passphrase
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"✅ Credenciais salvas para: {user.email}")
        
        return jsonify({'message': 'Credenciais salvas com sucesso'}), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar credenciais: {e}")
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/get-credentials', methods=['GET'])
@require_login
def get_credentials():
    """Buscar credenciais da API Bitget do usuário"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se tem credenciais
        has_credentials = bool(user.api_key and user.api_secret and user.api_passphrase)
        
        if not has_credentials:
            return jsonify({
                'success': False,
                'message': 'Nenhuma credencial encontrada',
                'has_credentials': False
            }), 200
        
        # Retornar credenciais (em produção, descriptografar)
        return jsonify({
            'success': True,
            'message': 'Credenciais encontradas',
            'has_credentials': True,
            'credentials': {
                'apiKey': user.api_key,
                'apiSecret': user.api_secret,
                'passphrase': user.api_passphrase
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar credenciais: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/reconnect-api', methods=['POST'])
@require_login
def reconnect_api():
    """Reconectar API usando credenciais salvas"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se tem credenciais
        if not (user.api_key and user.api_secret and user.api_passphrase):
            return jsonify({
                'success': False,
                'error': 'Nenhuma credencial encontrada. Configure suas credenciais primeiro.',
                'redirect_to_config': True
            }), 400
        
        # Simular teste de conexão (em produção, testar com API Bitget real)
        logger.info(f"✅ API reconectada para usuário: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'API reconectada com sucesso!',
            'data': {
                'api_status': 'connected',
                'user_email': user.email,
                'reconnected_at': datetime.now().isoformat(),
                'credentials_available': True
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro no reconnect_api: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@app.route('/api/credentials-status', methods=['GET'])
@require_login
def credentials_status():
    """Verificar status das credenciais"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        has_credentials = bool(user.api_key and user.api_secret and user.api_passphrase)
        
        return jsonify({
            'has_credentials': has_credentials,
            'api_configured': has_credentials,
            'last_updated': user.updated_at.isoformat() if user.updated_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# ROTAS ADMINISTRATIVAS
# ================================

@app.route('/api/admin/users')
@require_admin
def list_users():
    """Listar todos os usuários (admin)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar usuários: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================
# TRATAMENTO DE ERROS
# ================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Método não permitido'}), 405

# ================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ================================

# Inicializar banco de dados
init_database()

# Variável para o Render/WSGI
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Iniciando BigWhale Backend...")
    print(f"🌐 Porta: {port}")
    print(f"🔧 Ambiente: {'Render' if os.environ.get('RENDER') else 'Local'}")
    print("📧 Credenciais padrão:")
    print("   admin@bigwhale.com / Raikamaster1@")
    print("   willian@lexxusadm.com.br / Bigwhale202021@")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Sempre False em produção
    ) 