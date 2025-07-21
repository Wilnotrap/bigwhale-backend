#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correção do sistema backend
Corrige problemas de banco de dados e configuração
"""

import os
import sys
import sqlite3
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def create_instance_directory():
    """Cria o diretório instance se não existir"""
    instance_dir = os.path.join(backend_dir, 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir, exist_ok=True)
        print(f"✅ Diretório criado: {instance_dir}")
    else:
        print(f"✅ Diretório já existe: {instance_dir}")
    return instance_dir

def initialize_database():
    """Inicializa o banco de dados SQLite"""
    try:
        # Importar Flask app
        from app_corrigido import create_app
        
        app = create_app()
        
        with app.app_context():
            from database import db
            
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas do banco de dados criadas")
            
            # Verificar se as tabelas foram criadas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tabelas encontradas: {tables}")
            
            # Criar usuários admin se não existirem
            from models.user import User
            from werkzeug.security import generate_password_hash
            
            admin_users = [
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
                }
            ]
            
            for admin_data in admin_users:
                existing_user = User.query.filter_by(email=admin_data['email']).first()
                if not existing_user:
                    user = User(
                        full_name=admin_data['full_name'],
                        email=admin_data['email'],
                        password_hash=generate_password_hash(admin_data['password']),
                        is_active=True,
                        is_admin=admin_data['is_admin']
                    )
                    db.session.add(user)
                    print(f"✅ Usuário admin criado: {admin_data['email']}")
                else:
                    print(f"✅ Usuário admin já existe: {admin_data['email']}")
            
            db.session.commit()
            print("✅ Banco de dados inicializado com sucesso")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        import traceback
        traceback.print_exc()

def check_database_integrity():
    """Verifica a integridade do banco de dados"""
    try:
        db_path = os.path.join(backend_dir, 'instance', 'site.db')
        
        if not os.path.exists(db_path):
            print("⚠️  Banco de dados não existe, será criado")
            return False
        
        # Conectar ao banco e verificar tabelas
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Tabelas no banco: {[table[0] for table in tables]}")
        
        # Verificar tabela users
        if ('users',) in tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 Usuários cadastrados: {user_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def fix_permissions():
    """Corrige permissões de arquivos"""
    try:
        instance_dir = os.path.join(backend_dir, 'instance')
        
        # Garantir que o diretório instance tenha permissões corretas
        if os.path.exists(instance_dir):
            os.chmod(instance_dir, 0o755)
            print("✅ Permissões do diretório instance corrigidas")
        
        # Verificar arquivo de banco
        db_path = os.path.join(instance_dir, 'site.db')
        if os.path.exists(db_path):
            os.chmod(db_path, 0o644)
            print("✅ Permissões do banco de dados corrigidas")
            
    except Exception as e:
        print(f"⚠️  Erro ao corrigir permissões: {e}")

def main():
    print("🔧 CORREÇÃO DO SISTEMA BACKEND")
    print("=" * 40)
    
    # 1. Criar diretório instance
    create_instance_directory()
    
    # 2. Verificar integridade do banco
    db_ok = check_database_integrity()
    
    # 3. Inicializar banco se necessário
    if not db_ok:
        print("\n🔄 Inicializando banco de dados...")
        initialize_database()
    
    # 4. Corrigir permissões
    fix_permissions()
    
    print("\n✅ CORREÇÃO CONCLUÍDA!")
    print("\n📋 CREDENCIAIS DE TESTE:")
    print("   admin@bigwhale.com / Raikamaster1@")
    print("   willian@lexxusadm.com.br / Bigwhale202021@")
    print("\n🚀 Para iniciar o backend:")
    print("   python app_corrigido.py")

if __name__ == '__main__':
    main()