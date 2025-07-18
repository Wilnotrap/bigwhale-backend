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
            
            # Primeiro, criar todas as tabelas se não existirem
            print("📝 Criando tabelas se necessário...")
            db.create_all()
            print("✅ Tabelas verificadas/criadas!")
            
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
                    ELSE
                        RAISE NOTICE 'Coluna nautilus_trader_id já existe';
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
                    ELSE
                        RAISE NOTICE 'Coluna operational_balance_usd já existe';
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
                    ELSE
                        RAISE NOTICE 'Coluna api_configured já existe';
                    END IF;
                END $$;
                """,
                
                # Adicionar coluna updated_at se não existir
                """
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='updated_at') THEN
                        ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                        RAISE NOTICE 'Coluna updated_at adicionada';
                    ELSE
                        RAISE NOTICE 'Coluna updated_at já existe';
                    END IF;
                END $$;
                """,
                
                # Adicionar coluna commission_rate se não existir
                """
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='commission_rate') THEN
                        ALTER TABLE users ADD COLUMN commission_rate FLOAT DEFAULT 0.5;
                        RAISE NOTICE 'Coluna commission_rate adicionada';
                    ELSE
                        RAISE NOTICE 'Coluna commission_rate já existe';
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
                    print(f"⚠️  Migração {i} falhou: {e}")
                    db.session.rollback()
            
            print("🎉 Migrações concluídas!")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    migrate_database()