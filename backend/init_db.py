#!/usr/bin/env python3
"""
Script para inicializar o banco de dados com todas as tabelas
"""
import os
from app import create_app
from database import db

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    app = create_app()
    
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Banco de dados inicializado com sucesso!")
            print("✅ Todas as tabelas foram criadas!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")

if __name__ == "__main__":
    init_database()