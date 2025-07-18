#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração simples para o banco de dados
"""

import os
from sqlalchemy import text
from database import db
from app import create_app

def migrate_database():
    """Executa migrações necessárias no banco de dados"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Executando migrações do banco de dados...")
            
            # Lista de comandos SQL para executar
            migrations = [
                # Adicionar coluna nautilus_trader_id se não existir
                """
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='nautilus_trader_id') THEN
                        ALTER TABLE users ADD COLUMN nautilus_trader_id VARCHAR(120);
                        RAISE NOTICE 'Coluna nautilus_trader_id adicionada';
                    END IF;
                END $$;
                """,
                
                # Adicionar coluna operational_balance_usd se não existir
                """
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='operational_balance_usd') THEN
                        ALTER TABLE users ADD COLUMN operational_balance_usd FLOAT DEFAULT 0.0;
                        RAISE NOTICE 'Coluna operational_balance_usd adicionada';
                    END IF;
                END $$;
                """,
                
                # Adicionar coluna api_configured se não existir
                """
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='api_configured') THEN
                        ALTER TABLE users ADD COLUMN api_configured BOOLEAN DEFAULT FALSE;
                        RAISE NOTICE 'Coluna api_configured adicionada';
                    END IF;
                END $$;
                """
            ]
            
            # Executar cada migração
            for i, migration in enumerate(migrations, 1):
                try:
                    print(f"📝 Executando migração {i}...")
                    db.session.execute(text(migration))
                    db.session.commit()
                    print(f"✅ Migração {i} executada com sucesso!")
                    
                except Exception as e:
                    print(f"⚠️  Migração {i} falhou (pode já estar aplicada): {e}")
                    db.session.rollback()
            
            print("🎉 Migrações concluídas!")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    migrate_database()