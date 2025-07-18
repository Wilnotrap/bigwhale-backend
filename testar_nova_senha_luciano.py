#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o login do usuário Luciano com a nova senha
"""

import requests
import sqlite3
import os
from werkzeug.security import check_password_hash

def testar_senha_banco():
    """Testa a senha diretamente no banco de dados"""
    email = "luciano.curty@gmail.com"
    senha = "Nautilus2025@"
    
    db_path = r"C:\Nautilus Aut\RetesteProjeto\backend\instance\site.db"
    
    if os.path.exists(db_path):
        print(f"🔍 Testando senha no banco: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Buscar o usuário e sua senha hash
            cursor.execute("SELECT id, full_name, email, password_hash, is_active FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user:
                user_id, full_name, user_email, password_hash, is_active = user
                print(f"✅ Usuário encontrado:")
                print(f"   - ID: {user_id}")
                print(f"   - Nome: {full_name}")
                print(f"   - Email: {user_email}")
                print(f"   - Ativo: {'Sim' if is_active else 'Não'}")
                print(f"   - Hash: {password_hash[:30]}...")
                
                # Testar a senha
                if check_password_hash(password_hash, senha):
                    print(f"✅ Senha CORRETA! Login funcionará.")
                    return True
                else:
                    print(f"❌ Senha INCORRETA! Login falhará.")
                    return False
            else:
                print(f"❌ Usuário {email} não encontrado")
                return False
                
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao testar senha: {str(e)}")
            return False
    else:
        print(f"❌ Banco não encontrado: {db_path}")
        return False

def testar_login_api():
    """Testa o login via API local"""
    email = "luciano.curty@gmail.com"
    senha = "Nautilus2025@"
    
    # URL do backend local
    login_url = "http://localhost:5000/auth/login"
    
    print(f"\n🌐 Testando login via API: {login_url}")
    
    try:
        # Dados do login
        login_data = {
            "email": email,
            "password": senha
        }
        
        # Fazer requisição de login
        response = requests.post(login_url, json=login_data, timeout=10)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login bem-sucedido via API!")
            print(f"📄 Resposta: {data}")
            return True
        else:
            print(f"❌ Login falhou via API")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️  Servidor não está rodando em {login_url}")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar login via API: {str(e)}")
        return False

def main():
    print("🔐 TESTE DE NOVA SENHA - LUCIANO CURTY")
    print("="*50)
    print(f"📧 Email: luciano.curty@gmail.com")
    print(f"🔑 Senha: Nautilus2025@")
    print("="*50)
    
    # Teste 1: Verificar senha no banco
    print("\n🧪 TESTE 1: Verificação direta no banco de dados")
    banco_ok = testar_senha_banco()
    
    # Teste 2: Testar login via API
    print("\n🧪 TESTE 2: Login via API")
    api_ok = testar_login_api()
    
    # Resumo
    print("\n" + "="*50)
    print("📋 RESUMO DOS TESTES:")
    print(f"🔍 Senha no banco: {'✅ OK' if banco_ok else '❌ FALHOU'}")
    print(f"🌐 Login via API: {'✅ OK' if api_ok else '❌ FALHOU'}")
    
    if banco_ok:
        print("\n🎉 A senha foi alterada com sucesso!")
        print("💡 O usuário Luciano pode fazer login com: Nautilus2025@")
    else:
        print("\n⚠️  Há problemas com a alteração da senha.")

if __name__ == "__main__":
    main()