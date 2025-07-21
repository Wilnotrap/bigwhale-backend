#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar conta demo no sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from models.user import User
from werkzeug.security import generate_password_hash
from flask import Flask

def create_app():
    """Cria aplicação Flask para inicialização"""
    app = Flask(__name__)
    
    # Configuração básica
    app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'
    # Configurar caminho do banco de dados
    db_path = os.path.join(os.getcwd(), 'backend', 'instance', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Garantir que o diretório instance existe
    instance_dir = os.path.join(os.getcwd(), 'backend', 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    db.init_app(app)
    return app

def init_demo_account():
    """Inicializa a conta demo no banco de dados"""
    app = create_app()
    
    with app.app_context():
        try:
            # Criar tabelas se não existirem
            db.create_all()
            print("✅ Tabelas do banco de dados criadas/verificadas")
            
            # Credenciais para criar/atualizar
            users_data = [
                {
                    'email': 'admin@bigwhale.com',
                    'password': 'Raikamaster1@',
                    'full_name': 'Admin BigWhale',
                    'is_admin': True
                },
                {
                    'email': 'willian@lexxusadm.com.br',
                    'password': 'Bigwhale202021@',
                    'full_name': 'Willian Admin',
                    'is_admin': True
                },
                {
                    'email': 'financeiro@lexxusadm.com.br',
                    'password': 'FinanceiroDemo2025@',
                    'full_name': 'Conta Demo Financeiro',
                    'is_admin': False
                }
            ]
            
            for user_data in users_data:
                # Verificar se usuário já existe
                existing_user = User.query.filter_by(email=user_data['email']).first()
                
                if existing_user:
                    # Atualizar senha e dados
                    existing_user.password_hash = generate_password_hash(user_data['password'])
                    existing_user.full_name = user_data['full_name']
                    existing_user.is_admin = user_data['is_admin']
                    existing_user.is_active = True
                    print(f"✅ Usuário {user_data['email']} atualizado")
                else:
                    # Criar novo usuário
                    from datetime import datetime
                    new_user = User(
                        email=user_data['email'],
                        password_hash=generate_password_hash(user_data['password']),
                        full_name=user_data['full_name'],
                        is_admin=user_data['is_admin'],
                        is_active=True,
                        created_at=datetime.now()
                    )
                    db.session.add(new_user)
                    print(f"✅ Usuário {user_data['email']} criado")
            
            # Salvar alterações
            db.session.commit()
            print("\n🎉 Conta demo inicializada com sucesso!")
            print("\n📧 Credenciais disponíveis:")
            print("   admin@bigwhale.com / Raikamaster1@ (ADMIN)")
            print("   willian@lexxusadm.com.br / Bigwhale202021@ (ADMIN)")
            print("   financeiro@lexxusadm.com.br / FinanceiroDemo2025@ (DEMO)")
            
            # Verificar usuários criados
            total_users = User.query.count()
            print(f"\n📊 Total de usuários no sistema: {total_users}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar conta demo: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🚀 Inicializando conta demo...")
    success = init_demo_account()
    
    if success:
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Processo falhou!")
        sys.exit(1)