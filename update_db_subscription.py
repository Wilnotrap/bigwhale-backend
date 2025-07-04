#!/usr/bin/env python3
from app import create_app
from database import db
from models.user import User

def update_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Adicionar as novas colunas se não existirem
            db.engine.execute('ALTER TABLE users ADD COLUMN has_paid BOOLEAN DEFAULT 0')
            print("✅ Coluna has_paid adicionada")
        except:
            print("⚠️ Coluna has_paid já existe")
            
        try:
            db.engine.execute('ALTER TABLE users ADD COLUMN subscription_type VARCHAR(50)')
            print("✅ Coluna subscription_type adicionada")
        except:
            print("⚠️ Coluna subscription_type já existe")
            
        try:
            db.engine.execute('ALTER TABLE users ADD COLUMN subscription_start_date DATETIME')
            print("✅ Coluna subscription_start_date adicionada")
        except:
            print("⚠️ Coluna subscription_start_date já existe")
            
        try:
            db.engine.execute('ALTER TABLE users ADD COLUMN subscription_end_date DATETIME')
            print("✅ Coluna subscription_end_date adicionada")
        except:
            print("⚠️ Coluna subscription_end_date já existe")
            
        try:
            db.engine.execute('ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)')
            print("✅ Coluna stripe_customer_id adicionada")
        except:
            print("⚠️ Coluna stripe_customer_id já existe")
            
        try:
            db.engine.execute('ALTER TABLE users ADD COLUMN stripe_subscription_id VARCHAR(255)')
            print("✅ Coluna stripe_subscription_id adicionada")
        except:
            print("⚠️ Coluna stripe_subscription_id já existe")
        
        print("🎯 Migração concluída!")

if __name__ == '__main__':
    update_database()