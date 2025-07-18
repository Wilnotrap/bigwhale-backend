#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar colunas ausentes no banco de dados de produção
"""

import os
import sys
from sqlalchemy import text, inspect
from database import db
from app import create_app

def check_and_create_columns():
    """Verifica e cria colunas ausentes na tabela users"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Conectar ao banco
            inspector = inspect(db.engine)
            
            # Verificar se a tabela users existe
            if not inspector.has_table('users'):
                print("❌ Tabela 'users' não encontrada!")
                return False
            
            # Obter colunas existentes
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"✅ Colunas existentes: {existing_columns}")
            
            # Colunas que precisam existir
            required_columns = {
                'nautilus_trader_id': 'VARCHAR(120)',
                'operational_balance_usd': 'FLOAT DEFAULT 0.0',
                'api_configured': 'BOOLEAN DEFAULT FALSE'
            }
            
            # Verificar e adicionar colunas ausentes
            for column_name, column_type in required_columns.items():
                if column_name not in existing_columns:
                    print(f"🔧 Adicionando coluna ausente: {column_name}")
                    
                    try:
                        # Comando SQL para adicionar coluna
                        sql_command = f"ALTER TABLE users ADD COLUMN {column_name} {column_type};"
                        db.session.execute(text(sql_command))
                        db.session.commit()
                        print(f"✅ Coluna {column_name} adicionada com sucesso!")
                        
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna {column_name}: {e}")
                        db.session.rollback()
                        return False
                else:
                    print(f"✅ Coluna {column_name} já existe")
            
            print("🎉 Todas as colunas necessárias estão presentes!")
            return True
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Iniciando verificação e criação de colunas...")
    success = check_and_create_columns()
    
    if success:
        print("✅ Script executado com sucesso!")
        sys.exit(0)
    else:
        print("❌ Script falhou!")
        sys.exit(1)