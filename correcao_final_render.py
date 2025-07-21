#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO FINAL PARA O RENDER
Este script deve ser executado diretamente no ambiente do Render
"""

import os
import sys
import subprocess
import sqlite3
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def instalar_psycopg2():
    """Instala psycopg2-binary diretamente"""
    try:
        logger.info("Verificando psycopg2...")
        
        # Verificar se já está instalado
        try:
            import psycopg2
            logger.info("✅ psycopg2 já está instalado")
            return True
        except ImportError:
            pass
        
        # Instalar psycopg2-binary
        logger.info("Instalando psycopg2-binary...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "psycopg2-binary==2.9.9"])
        
        # Verificar se foi instalado
        try:
            import psycopg2
            logger.info("✅ psycopg2-binary instalado com sucesso!")
            return True
        except ImportError:
            logger.error("❌ Falha ao instalar psycopg2-binary")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao instalar psycopg2-binary: {e}")
        return False

def criar_tabelas_direto():
    """Cria todas as tabelas necessárias diretamente via SQLite"""
    try:
        logger.info("Criando tabelas diretamente...")
        
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
        
        conn.commit()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        logger.info(f"Tabelas no banco: {tables}")
        
        conn.close()
        logger.info("✅ Todas as tabelas criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def criar_rota_raiz():
    """Cria um arquivo app.py com uma rota raiz simples"""
    try:
        logger.info("Criando arquivo app.py com rota raiz...")
        
        conteudo = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Aplicação Flask simples com rota raiz
\"\"\"

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "BigWhale Backend API",
        "status": "running"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""
        
        # Salvar arquivo
        with open('app_simples.py', 'w') as f:
            f.write(conteudo)
        
        logger.info("✅ Arquivo app_simples.py criado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar arquivo app.py: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=== INICIANDO CORREÇÃO FINAL PARA O RENDER ===")
    
    # Instalar psycopg2
    instalar_psycopg2()
    
    # Criar tabelas diretamente
    criar_tabelas_direto()
    
    # Criar rota raiz
    criar_rota_raiz()
    
    logger.info("=== CORREÇÃO FINAL CONCLUÍDA ===")
    logger.info("Execute python app_simples.py para iniciar uma aplicação simples")

if __name__ == "__main__":
    main()