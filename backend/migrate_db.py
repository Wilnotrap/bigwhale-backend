#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração simples para o banco de dados
"""

import os
from sqlalchemy import text, inspect
from database import db
from app import create_app

def migrate_database():
    """Executa migrações necessárias no banco de dados"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Executando migrações do banco de dados...")
            
            # Primeiro, criar todas as tabelas se não existirem
            print("📝 Criando tabelas se necessário...")
            db.create_all()
            print("✅ Tabelas verificadas/criadas!")
            
            # Criar inspector para verificar estrutura do banco
            inspector = inspect(db.engine)
            
            # Migrar tabela USERS
            print("👤 Verificando tabela USERS...")
            if inspector.has_table('users'):
                existing_users_columns = [col['name'] for col in inspector.get_columns('users')]
                print(f"📋 Colunas existentes em users: {existing_users_columns}")
                
                users_columns_to_add = [
                    ('nautilus_trader_id', 'VARCHAR(120)'),
                    ('operational_balance_usd', 'FLOAT DEFAULT 0.0'),
                    ('api_configured', 'BOOLEAN DEFAULT FALSE'),
                    ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('commission_rate', 'FLOAT DEFAULT 0.5')
                ]
                
                for column_name, column_type in users_columns_to_add:
                    if column_name not in existing_users_columns:
                        try:
                            print(f"➕ Adicionando coluna users.{column_name}")
                            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type};"
                            db.session.execute(text(sql))
                            db.session.commit()
                            print(f"✅ Coluna users.{column_name} adicionada!")
                            
                        except Exception as e:
                            print(f"❌ Erro ao adicionar users.{column_name}: {e}")
                            db.session.rollback()
                    else:
                        print(f"ℹ️  Coluna users.{column_name} já existe")
            
            # Migrar tabela TRADES
            print("📊 Verificando tabela TRADES...")
            if inspector.has_table('trades'):
                existing_trades_columns = [col['name'] for col in inspector.get_columns('trades')]
                print(f"📋 Colunas existentes em trades: {existing_trades_columns}")
                
                trades_columns_to_add = [
                    ('takes_hit', 'INTEGER DEFAULT 0'),
                    ('margin', 'FLOAT'),
                    ('fees', 'FLOAT DEFAULT 0.0'),
                    ('bitget_position_id', 'VARCHAR(100)'),
                    ('roe', 'FLOAT')
                ]
                
                for column_name, column_type in trades_columns_to_add:
                    if column_name not in existing_trades_columns:
                        try:
                            print(f"➕ Adicionando coluna trades.{column_name}")
                            sql = f"ALTER TABLE trades ADD COLUMN {column_name} {column_type};"
                            db.session.execute(text(sql))
                            db.session.commit()
                            print(f"✅ Coluna trades.{column_name} adicionada!")
                            
                        except Exception as e:
                            print(f"❌ Erro ao adicionar trades.{column_name}: {e}")
                            db.session.rollback()
                    else:
                        print(f"ℹ️  Coluna trades.{column_name} já existe")
            
            print("🎉 Migrações concluídas!")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = migrate_database()
    if not success:
        exit(1)