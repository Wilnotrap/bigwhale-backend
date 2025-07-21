#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar o usuário demo
"""

import os
import sys
from flask import Flask
from database import db
from models.user import User

def create_app():
    """Cria aplicação Flask para inicialização"""
    app = Flask(__name__)
    
    # Configuração básica
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurar banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Render usa postgresql:// em vez de postgres://
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url or f'sqlite:///{db_path}'
    
    # Carregar variáveis de ambiente do arquivo .env se existir
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    db.init_app(app)
    return app

def init_demo_user():
    """Inicializa o usuário demo"""
    app = create_app()
    
    with app.app_context():
        try:
            # Criar tabelas se não existirem
            db.create_all()
            
            # Verificar se o usuário demo já existe
            demo_user = User.query.filter_by(email='financeiro@lexxusadm.com.br').first()
            
            if demo_user:
                print(f"Usuário demo já existe: {demo_user.full_name}")
                print(f"Saldo atual: ${demo_user.operational_balance_usd}")
                
                # Atualizar saldo se necessário
                if demo_user.operational_balance_usd != 600.0:
                    demo_user.operational_balance_usd = 600.0
                    db.session.commit()
                    print(f"Saldo atualizado para: $600.00")
                
                return True
            
            # Criar usuário demo
            demo_user = User(
                email='financeiro@lexxusadm.com.br',
                full_name='Conta Demo Financeiro',
                is_admin=False,
                is_active=True,
                operational_balance_usd=600.0
            )
            
            # Definir senha
            demo_user.set_password('FinanceiroDemo2025@')
            
            # Salvar no banco de dados
            db.session.add(demo_user)
            db.session.commit()
            
            print(f"Usuário demo criado com sucesso:")
            print(f"Email: financeiro@lexxusadm.com.br")
            print(f"Nome: Conta Demo Financeiro")
            print(f"Saldo: $600.00")
            
            return True
            
        except Exception as e:
            print(f"Erro ao inicializar usuário demo: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_demo_user()
    
    if success:
        print("\n✅ Usuário demo inicializado com sucesso!")
    else:
        print("\n❌ Erro ao inicializar usuário demo!")
        sys.exit(1)