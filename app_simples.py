#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação Flask simples com rota raiz
"""

import os
import sys
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

# Verificar e criar tabela active_signals se necessário
try:
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
    conn.commit()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    print(f"Tabelas no banco: {tables}")
    
    conn.close()
except Exception as e:
    print(f"Erro ao criar tabela: {e}")

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
        "database": tabelas_info
    }), 200

@app.route('/api/test')
def test():
    return jsonify({
        "message": "API de teste funcionando!",
        "status": "ok"
    }), 200

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-07-21T11:30:00Z",
        "environment": "Render",
        "message": "Sistema BigWhale funcionando corretamente"
    }), 200

if __name__ == '__main__':
    # Instalar psycopg2 se necessário
    try:
        import psycopg2
    except ImportError:
        import subprocess
        print("Instalando psycopg2-binary...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)