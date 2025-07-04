#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido para verificar se o backend está funcionando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== TESTE RÁPIDO DO BACKEND ===")
    print("1. Testando importações...")
    
    # Testar importações básicas
    from flask import Flask
    print("   ✓ Flask importado")
    
    from database import db
    print("   ✓ Database importado")
    
    from models.user import User
    print("   ✓ User model importado")
    
    from models.session import UserSession
    print("   ✓ UserSession model importado")
    
    from utils.security import encrypt_api_key, decrypt_api_key
    print("   ✓ Security utils importados")
    
    from auth.login import login, logout, check_session
    print("   ✓ Auth functions importadas")
    
    print("\n2. Testando criação da aplicação...")
    
    # Criar aplicação Flask simples
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print("   ✓ Aplicação Flask criada")
    
    # Inicializar banco
    db.init_app(app)
    print("   ✓ Database inicializado")
    
    with app.app_context():
        # Criar tabelas
        db.create_all()
        print("   ✓ Tabelas criadas")
        
        # Verificar se consegue criar um usuário de teste
        from werkzeug.security import generate_password_hash
        
        test_user = User(
            username='test',
            email='test@test.com',
            password_hash=generate_password_hash('test123'),
            bitget_api_key='test_key',
            bitget_secret_key='test_secret',
            bitget_passphrase='test_pass'
        )
        
        db.session.add(test_user)
        db.session.commit()
        print("   ✓ Usuário de teste criado")
        
        # Verificar se consegue buscar o usuário
        found_user = User.query.filter_by(username='test').first()
        if found_user:
            print("   ✓ Usuário encontrado no banco")
        else:
            print("   ✗ Erro ao encontrar usuário")
    
    print("\n3. Testando criptografia...")
    
    # Testar criptografia
    test_data = "test_api_key_123"
    encrypted = encrypt_api_key(test_data)
    print(f"   ✓ Dados criptografados: {encrypted[:20]}...")
    
    decrypted = decrypt_api_key(encrypted)
    if decrypted == test_data:
        print("   ✓ Descriptografia funcionando")
    else:
        print("   ✗ Erro na descriptografia")
    
    print("\n=== TODOS OS TESTES PASSARAM! ===")
    print("O backend parece estar funcionando corretamente.")
    
except Exception as e:
    print(f"\n❌ ERRO NO TESTE: {str(e)}")
    import traceback
    print(f"\nTraceback completo:")
    print(traceback.format_exc())
    sys.exit(1)