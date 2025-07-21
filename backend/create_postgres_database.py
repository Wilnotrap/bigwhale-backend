#!/usr/bin/env python3
"""
Script para criar banco PostgreSQL diretamente com todas as tabelas
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_postgres_database():
    """Cria o banco PostgreSQL e todas as tabelas"""
    
    # Configurações do PostgreSQL (Render)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'bigwhale_db')
    
    print(f"🔄 Conectando ao PostgreSQL...")
    print(f"   Host: {DB_HOST}")
    print(f"   Port: {DB_PORT}")
    print(f"   User: {DB_USER}")
    print(f"   Database: {DB_NAME}")
    
    try:
        # Conectar ao PostgreSQL (sem especificar database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Criar database se não existir
        print("🏗️ Criando database...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✅ Database '{DB_NAME}' criado!")
        else:
            print(f"✅ Database '{DB_NAME}' já existe!")
        
        cursor.close()
        conn.close()
        
        # Conectar ao database específico
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Criar tabela users
        print("👥 Criando tabela users...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(100),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar tabela user_sessions
        print("🔐 Criando tabela user_sessions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                session_token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        # Criar tabela trades
        print("💰 Criando tabela trades...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                entry_price DECIMAL(20,8) NOT NULL,
                exit_price DECIMAL(20,8),
                quantity DECIMAL(20,8) NOT NULL,
                pnl DECIMAL(20,8),
                status VARCHAR(20) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP
            )
        """)
        
        # Criar tabela invite_codes
        print("🎫 Criando tabela invite_codes...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invite_codes (
                id SERIAL PRIMARY KEY,
                code VARCHAR(20) UNIQUE NOT NULL,
                created_by INTEGER REFERENCES users(id),
                used_by INTEGER REFERENCES users(id),
                is_used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP
            )
        """)
        
        # Criar tabela active_signals (COMPLETA)
        print("📊 Criando tabela active_signals...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_signals (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                symbol VARCHAR(50) NOT NULL,
                side VARCHAR(10) NOT NULL,
                entry_price DECIMAL(20,8) NOT NULL,
                targets_json TEXT,
                targets_hit INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'active',
                strategy VARCHAR(50),
                stop_loss DECIMAL(20,8),
                take_profit DECIMAL(20,8),
                position_size DECIMAL(20,8),
                leverage INTEGER,
                margin_mode VARCHAR(20),
                unrealized_pnl DECIMAL(20,8),
                mark_price DECIMAL(20,8),
                liquidation_price DECIMAL(20,8),
                margin_ratio DECIMAL(20,8),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Commit das mudanças
        conn.commit()
        
        print("✅ Todas as tabelas criadas com sucesso!")
        print("📋 Tabelas criadas:")
        print("   - users")
        print("   - user_sessions") 
        print("   - trades")
        print("   - invite_codes")
        print("   - active_signals")
        
        # Verificar tabelas criadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Total de tabelas: {len(tables)}")
        for table in tables:
            print(f"   ✅ {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("🎉 Banco PostgreSQL configurado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    create_postgres_database() 