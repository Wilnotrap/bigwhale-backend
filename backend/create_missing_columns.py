#!/usr/bin/env python3
"""
Script para criar colunas que faltam na tabela users
"""
import os
from flask import Flask
from database import db
from sqlalchemy import text

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def add_missing_columns():
    """Adiciona colunas que faltam na tabela users"""
    app = create_app()
    
    with app.app_context():
        try:
            # Lista de colunas para verificar/adicionar
            columns_to_add = [
                ('nautilus_trader_id', 'VARCHAR(120)'),
                ('operational_balance_usd', 'FLOAT DEFAULT 0.0'),
                ('commission_rate', 'FLOAT DEFAULT 0.5'),
                ('api_configured', 'BOOLEAN DEFAULT FALSE')
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    # Tentar adicionar a coluna
                    sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type};"
                    db.session.execute(text(sql))
                    db.session.commit()
                    print(f"✅ Coluna {column_name} adicionada com sucesso")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print(f"ℹ️  Coluna {column_name} já existe")
                    else:
                        print(f"❌ Erro ao adicionar coluna {column_name}: {e}")
                    db.session.rollback()
            
            print("🎉 Migração concluída!")
            
        except Exception as e:
            print(f"❌ Erro geral na migração: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_missing_columns()