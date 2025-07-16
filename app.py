#!/usr/bin/env python3
import os
import logging
import hashlib
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# CORS apenas para produção
CORS(app, 
     origins=['https://bwhale.site'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'],
     supports_credentials=True)

# Configuração do banco - APENAS POSTGRESQL EM PRODUÇÃO
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.error("DATABASE_URL não configurado! Deploy apenas em produção.")
    DATABASE_URL = "postgresql://dummy"

# Corrigir URL do PostgreSQL
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

logger.info(f"Usando PostgreSQL: {DATABASE_URL[:50]}...")

# Chave simples para dados API (base64)
import base64

def init_database():
    """Inicializar banco PostgreSQL"""
    try:
        conn = psycopg.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Criar tabela users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                bitget_api_key_encrypted TEXT,
                bitget_api_secret_encrypted TEXT,
                bitget_passphrase_encrypted TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco PostgreSQL inicializado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")

def get_db_connection():
    """Obter conexão PostgreSQL"""
    conn = psycopg.connect(DATABASE_URL)
    conn.autocommit = False
    return conn

def execute_query(cursor, query, params=None):
    """Executar query PostgreSQL"""
    # PostgreSQL usa %s
    pg_query = query.replace('?', '%s')
    cursor.execute(pg_query, params or ())

def fetch_user_dict(row):
    """Converter resultado PostgreSQL em dicionário"""
    columns = ['id', 'full_name', 'email', 'password_hash', 
              'bitget_api_key_encrypted', 'bitget_api_secret_encrypted', 
              'bitget_passphrase_encrypted', 'is_admin', 'created_at']
    return dict(zip(columns, row))

def hash_password(password):
    """Hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verificar senha"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def encrypt_text(text):
    """Codificar texto em base64"""
    if not text:
        return None
    return base64.b64encode(text.encode()).decode()

def decrypt_text(encoded_text):
    """Decodificar texto base64"""
    if not encoded_text:
        return None
    try:
        return base64.b64decode(encoded_text.encode()).decode()
    except:
        return None

# Inicializar banco
init_database()

# Rotas
@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': 'Nautilus Automação API',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'database_type': 'PostgreSQL',
            'users_count': user_count,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        execute_query(cursor, 'SELECT * FROM users WHERE email = ?', (email,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            user = fetch_user_dict(user_row)
            if verify_password(password, user['password_hash']):
                return jsonify({
                    'message': 'Login realizado com sucesso',
                    'user': {
                        'id': user['id'],
                        'name': user['full_name'],
                        'email': user['email'],
                        'is_admin': bool(user['is_admin'])
                    }
                })
        
        return jsonify({'error': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validar dados
        required_fields = ['full_name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se email já existe
        execute_query(cursor, 'SELECT id FROM users WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Criptografar credenciais da API se fornecidas
        api_key_encrypted = encrypt_text(data.get('bitget_api_key'))
        api_secret_encrypted = encrypt_text(data.get('bitget_api_secret'))
        passphrase_encrypted = encrypt_text(data.get('bitget_passphrase'))
        
        # Criar usuário
        execute_query(cursor, '''
            INSERT INTO users (full_name, email, password_hash, 
                             bitget_api_key_encrypted, bitget_api_secret_encrypted, bitget_passphrase_encrypted)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['full_name'],
            data['email'],
            hash_password(data['password']),
            api_key_encrypted,
            api_secret_encrypted,
            passphrase_encrypted
        ))
        
        # Obter ID do usuário criado
        cursor.execute('SELECT lastval()')
        user_id = cursor.fetchone()[0]
            
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': {
                'id': user_id,
                'name': data['full_name'],
                'email': data['email']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/auth/session', methods=['GET'])
def check_session():
    try:
        # Simular verificação de sessão
        user_id = request.headers.get('X-User-ID')
        
        # Se não há user_id, retornar não autenticado (sem erro 401)
        if not user_id:
            return jsonify({'authenticated': False})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        execute_query(cursor, 'SELECT * FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            user = fetch_user_dict(user_row)
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user['id'],
                    'name': user['full_name'],
                    'email': user['email'],
                    'is_admin': bool(user['is_admin'])
                }
            })
        else:
            return jsonify({'authenticated': False})
            
    except Exception as e:
        logger.error(f"Erro na verificação de sessão: {e}")
        return jsonify({'authenticated': False})

@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        # Simular usuário logado (em produção usar JWT/session)
        user_id = request.headers.get('X-User-ID', '1')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        execute_query(cursor, 'SELECT * FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user = fetch_user_dict(user_row)
        
        # Descriptografar credenciais
        credentials = {
            'api_key': decrypt_text(user['bitget_api_key_encrypted']),
            'api_secret': decrypt_text(user['bitget_api_secret_encrypted']),
            'passphrase': decrypt_text(user['bitget_passphrase_encrypted'])
        }
        
        # Remover valores None
        credentials = {k: v for k, v in credentials.items() if v is not None}
        
        return jsonify({
            'user': {
                'id': user['id'],
                'name': user['full_name'],
                'email': user['email'],
                'is_admin': bool(user['is_admin'])
            },
            'credentials': credentials
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/api/reconnect-api', methods=['POST'])
def reconnect_api():
    try:
        user_id = request.headers.get('X-User-ID', '1')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        execute_query(cursor, 'SELECT * FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user = fetch_user_dict(user_row)
        
        # Descriptografar credenciais
        api_key = decrypt_text(user['bitget_api_key_encrypted'])
        api_secret = decrypt_text(user['bitget_api_secret_encrypted'])
        passphrase = decrypt_text(user['bitget_passphrase_encrypted'])
        
        if not all([api_key, api_secret, passphrase]):
            return jsonify({'error': 'Credenciais API não configuradas'}), 400
        
        # Simular reconexão (em produção conectar com Bitget)
        return jsonify({
            'message': 'API reconectada com sucesso',
            'status': 'connected'
        })
        
    except Exception as e:
        logger.error(f"Erro ao reconectar API: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Alias para compatibilidade com gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
