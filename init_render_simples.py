#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicialização simples e direta para o Render
"""

import os
import sys
import sqlite3
import subprocess
from werkzeug.security import generate_password_hash

def main():
    print("=== INICIANDO INICIALIZAÇÃO SIMPLES ===")
    
    # 1. Instalar psycopg2 se necessário
    try:
        import psycopg2
        print("✅ psycopg2 já instalado")
    except ImportError:
        print("Instalando psycopg2-binary...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
        print("✅ psycopg2-binary instalado")
    
    # 2. Criar banco SQLite
    if os.environ.get('RENDER'):
        db_path = '/tmp/site.db'
    else:
        db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
    
    # Garantir diretório
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    print(f"Criando banco em: {db_path}")
    
    # Conectar e criar tabelas
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabela users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128),
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            operational_balance_usd FLOAT DEFAULT 0.0,
            bitget_api_key_encrypted TEXT,
            bitget_api_secret_encrypted TEXT,
            bitget_passphrase_encrypted TEXT
        )
    ''')
    
    # Tabela active_signals
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL,
            entry_price FLOAT NOT NULL,
            stop_loss FLOAT,
            take_profit FLOAT,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            closed_at DATETIME,
            user_id INTEGER,
            targets VARCHAR(500),
            targets_hit INTEGER DEFAULT 0
        )
    ''')
    
    # Outras tabelas necessárias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL,
            quantity FLOAT NOT NULL,
            price FLOAT NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            executed_at DATETIME
        )
    ''')
    
    conn.commit()
    
    # Verificar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"✅ Tabelas criadas: {tables}")
    
    # Criar usuário demo
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ('financeiro@lexxusadm.com.br',))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('FinanceiroDemo2025@')
        cursor.execute('''
            INSERT INTO users (full_name, email, password_hash, is_active, is_admin, operational_balance_usd)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Conta Demo Financeiro', 'financeiro@lexxusadm.com.br', password_hash, 1, 0, 600.0))
        conn.commit()
        print("✅ Usuário demo criado")
    else:
        print("✅ Usuário demo já existe")
    
    conn.close()
    print("=== INICIALIZAÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    main()