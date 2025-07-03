#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para identificar problemas no login do backend BigWhale
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from flask import Flask
from database import db
from models.user import User
from models.session import UserSession
from utils.security import encrypt_api_key, decrypt_api_key
from werkzeug.security import generate_password_hash
import traceback

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("\n=== TESTE DE CONEXÃO COM BANCO DE DADOS ===")
    try:
        # Criar app temporário
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_debug.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-key'
        app.config['AES_ENCRYPTION_KEY'] = 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789'
        
        db.init_app(app)
        
        with app.app_context():
            # Criar tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso")
            
            # Testar criação de usuário
            test_user = User(
                full_name="Teste Debug",
                email="debug@test.com",
                password_hash=generate_password_hash("test123"),
                is_active=True,
                is_admin=False
            )
            
            db.session.add(test_user)
            db.session.commit()
            print("✅ Usuário de teste criado com sucesso")
            
            # Testar busca de usuário
            found_user = User.query.filter_by(email="debug@test.com").first()
            if found_user:
                print("✅ Usuário encontrado na busca")
                print(f"   ID: {found_user.id}")
                print(f"   Nome: {found_user.full_name}")
                print(f"   Email: {found_user.email}")
            else:
                print("❌ Usuário não encontrado")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        traceback.print_exc()
        return False

def test_session_creation():
    """Testa a criação de sessões"""
    print("\n=== TESTE DE CRIAÇÃO DE SESSÃO ===")
    try:
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_debug.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-key'
        app.config['AES_ENCRYPTION_KEY'] = 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789'
        
        db.init_app(app)
        
        with app.app_context():
            # Buscar usuário de teste
            user = User.query.filter_by(email="debug@test.com").first()
            if not user:
                print("❌ Usuário de teste não encontrado")
                return False
                
            # Criar sessão
            session = UserSession.create_session(
                user_id=user.id,
                user_agent="Debug Test Agent",
                ip_address="127.0.0.1"
            )
            
            print("✅ Sessão criada com sucesso")
            print(f"   ID: {session.id}")
            print(f"   Token: {session.session_token[:20]}...")
            print(f"   User ID: {session.user_id}")
            
            # Testar busca de sessão ativa
            active_session = UserSession.get_active_session(session.session_token)
            if active_session:
                print("✅ Sessão ativa encontrada")
            else:
                print("❌ Sessão ativa não encontrada")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Erro na criação de sessão: {e}")
        traceback.print_exc()
        return False

def test_encryption():
    """Testa as funções de criptografia"""
    print("\n=== TESTE DE CRIPTOGRAFIA ===")
    try:
        app = Flask(__name__)
        app.config['AES_ENCRYPTION_KEY'] = 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789'
        
        with app.app_context():
            # Testar criptografia
            test_data = "test_api_key_12345"
            encrypted = encrypt_api_key(test_data)
            
            if encrypted:
                print("✅ Criptografia funcionando")
                print(f"   Original: {test_data}")
                print(f"   Criptografado: {encrypted[:50]}...")
                
                # Testar descriptografia
                decrypted = decrypt_api_key(encrypted)
                if decrypted == test_data:
                    print("✅ Descriptografia funcionando")
                    print(f"   Descriptografado: {decrypted}")
                else:
                    print(f"❌ Descriptografia falhou: {decrypted}")
                    return False
            else:
                print("❌ Criptografia falhou")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Erro na criptografia: {e}")
        traceback.print_exc()
        return False

def test_login_simulation():
    """Simula o processo de login completo"""
    print("\n=== SIMULAÇÃO DE LOGIN COMPLETO ===")
    try:
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_debug.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-key'
        app.config['AES_ENCRYPTION_KEY'] = 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789'
        
        db.init_app(app)
        
        with app.app_context():
            # Buscar usuário
            user = User.query.filter_by(email="debug@test.com").first()
            if not user:
                print("❌ Usuário não encontrado")
                return False
                
            print("✅ Usuário encontrado")
            
            # Verificar senha
            if user.check_password("test123"):
                print("✅ Senha verificada")
            else:
                print("❌ Senha incorreta")
                return False
                
            # Criar sessão
            new_session = UserSession.create_session(
                user_id=user.id,
                user_agent="Debug Login Test",
                ip_address="127.0.0.1"
            )
            print("✅ Nova sessão criada")
            
            # Simular descriptografia de credenciais (mesmo que vazias)
            api_key = decrypt_api_key(user.bitget_api_key_encrypted) if user.bitget_api_key_encrypted else None
            api_secret = decrypt_api_key(user.bitget_api_secret_encrypted) if user.bitget_api_secret_encrypted else None
            passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
            
            print("✅ Descriptografia de credenciais concluída")
            print(f"   API Key: {'Configurada' if api_key else 'Não configurada'}")
            print(f"   API Secret: {'Configurada' if api_secret else 'Não configurada'}")
            print(f"   Passphrase: {'Configurada' if passphrase else 'Não configurada'}")
            
            # Simular resposta de login
            response_data = {
                'message': 'Login realizado com sucesso',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_admin': user.is_admin,
                    'is_active': user.is_active,
                    'api_configured': bool(api_key and api_secret and passphrase),
                    'session_token': new_session.session_token
                }
            }
            
            print("✅ Simulação de login completa")
            print(f"   Response: {response_data}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na simulação de login: {e}")
        traceback.print_exc()
        return False

def cleanup():
    """Limpa arquivos de teste"""
    try:
        if os.path.exists('test_debug.db'):
            os.remove('test_debug.db')
            print("\n🧹 Arquivo de teste removido")
    except:
        pass

def main():
    """Executa todos os testes de diagnóstico"""
    print("🔍 DIAGNÓSTICO DO BACKEND BIGWHALE")
    print("=" * 50)
    
    tests = [
        ("Conexão com Banco de Dados", test_database_connection),
        ("Criação de Sessão", test_session_creation),
        ("Criptografia", test_encryption),
        ("Simulação de Login", test_login_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("💡 O problema pode estar na configuração do Render ou na rede.")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        print("💡 Verifique os erros acima para identificar o problema.")
    
    cleanup()

if __name__ == "__main__":
    main()