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
            
            # Verificar colunas existentes
            inspector = inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"📋 Colunas existentes: {existing_columns}")
            
            # Lista de colunas para adicionar
            columns_to_add = [
                ('nautilus_trader_id', 'VARCHAR(120)'),
                ('operational_balance_usd', 'FLOAT DEFAULT 0.0'),
                ('api_configured', 'BOOLEAN DEFAULT FALSE'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('commission_rate', 'FLOAT DEFAULT 0.5')
            ]
            
            # Adicionar colunas que não existem
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        print(f"➕ Adicionando coluna: {column_name}")
                        sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type};"
                        db.session.execute(text(sql))
                        db.session.commit()
                        print(f"✅ Coluna {column_name} adicionada com sucesso!")
                        
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna {column_name}: {e}")
                        db.session.rollback()
                else:
                    print(f"ℹ️  Coluna {column_name} já existe")
            
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