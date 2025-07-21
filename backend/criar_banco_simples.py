#!/usr/bin/env python3
"""
Script simples para criar o banco de dados e tabelas
"""

import os
import sqlite3
from sqlalchemy import create_engine, text

def criar_banco_simples():
    """Cria o banco de dados e as tabelas necessárias"""
    
    try:
        # Caminho do banco
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
        
        print(f"🗄️ Criando banco em: {db_path}")
        
        # Criar conexão SQLite direta
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar tabela active_signals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                targets TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Criar tabela users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Criar tabela invite_codes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invite_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                used_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                FOREIGN KEY (used_by) REFERENCES users (id)
            )
        ''')
        
        # Commit das alterações
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados criado com sucesso!")
        
        # Verificar se as tabelas foram criadas
        engine = create_engine(f'sqlite:///{db_path}')
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tabelas = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 Tabelas criadas ({len(tabelas)}):")
            for tabela in tabelas:
                print(f"  • {tabela}")
                
        print("\n🎉 Banco de dados pronto para uso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    criar_banco_simples() 