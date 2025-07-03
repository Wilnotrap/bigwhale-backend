#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from database import db
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import os
from datetime import timedelta

# --- Carregamento de Variáveis de Ambiente ---
# Carrega o arquivo .env da pasta raiz do projeto (um nível acima de 'backend')
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# --- Configuração do App Flask ---
app = Flask(__name__)

# --- Configurações de Segurança e Padrões de Desenvolvimento ---
# Define chaves padrão para o ambiente de desenvolvimento se não forem encontradas no .env.
# Isso garante que o app possa ser iniciado sem um arquivo .env configurado.
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-for-flask-sessions')
app.config['AES_ENCRYPTION_KEY'] = os.environ.get('AES_ENCRYPTION_KEY', 'a-safe-dev-key-must-be-32-bytes')


# --- Configuração do Banco de Dados ---
# Força o uso do banco de dados 'site.db' na pasta instance do backend.
# Isso garante consistência entre o servidor e todos os scripts auxiliares.
instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_dir, exist_ok=True)
db_path = os.path.join(instance_dir, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(f"✅ DATABASE_URI foi forçado para: {app.config['SQLALCHEMY_DATABASE_URI']}")

# --- Configurações Adicionais ---
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(app.instance_path, 'flask_session')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['DEBUG'] = os.environ.get('FLASK_ENV') != 'production'

# Garante que o diretório da instância e da sessão existam
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# --- Inicialização de Extensões ---
db.init_app(app)

# Inicializar Flask-Session
from flask_session import Session
Session(app)

CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://192.168.68.55:3000"]
    }
})

# --- Registro de Rotas (Blueprints) ---
from auth.routes import auth_bp
from api.dashboard import dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# --- Rota de Verificação de Saúde ---
@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

# --- Criação das Tabelas do Banco de Dados ---
with app.app_context():
    try:
        db.create_all()
        print("✅ Tabelas do banco de dados verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas do banco de dados: {e}")

# --- Execução do Servidor ---
if __name__ == '__main__':
    # O servidor é iniciado sem o processo de sincronização automática.
    print("🚀 Iniciando servidor sem sincronização automática...")
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])