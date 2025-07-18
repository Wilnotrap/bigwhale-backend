#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar login específico no ambiente de produção
"""

import requests
import json
from datetime import datetime
import hashlib
from werkzeug.security import check_password_hash

def testar_login_producao():
    """Testa o login específico no ambiente de produção"""
    
    print("🔍 TESTE DE LOGIN - AMBIENTE DE PRODUÇÃO")
    print("="*60)
    
    # URL de produção
    url_producao = "https://bigwhale-backend.onrender.com/api/auth/login"
    
    # Credenciais do Luciano
    credenciais = {
        "email": "luciano.curty@gmail.com",
        "password": "Nautilus2025@"
    }
    
    # Headers completos simulando o frontend
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://bwhale.site",
        "Referer": "https://bwhale.site/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }
    
    print(f"🌐 URL: {url_producao}")
    print(f"📧 Email: {credenciais['email']}")
    print(f"🔑 Senha: {'*' * len(credenciais['password'])}")
    
    try:
        # Teste 1: OPTIONS (preflight CORS)
        print("\n📋 TESTE 1: OPTIONS (CORS Preflight)")
        print("-" * 40)
        
        options_response = requests.options(
            url_producao, 
            headers={
                "Origin": "https://bwhale.site",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=15
        )
        
        print(f"✅ Status: {options_response.status_code}")
        print(f"📄 CORS Headers:")
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods', 
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Credentials'
        ]
        
        for header in cors_headers:
            value = options_response.headers.get(header, 'NÃO DEFINIDO')
            print(f"   {header}: {value}")
        
        # Teste 2: POST (login real)
        print("\n📋 TESTE 2: POST (Login Real)")
        print("-" * 40)
        
        response = requests.post(
            url_producao,
            json=credenciais,
            headers=headers,
            timeout=15
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        print(f"\n📄 Response Body:")
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print(f"Texto: {response.text}")
        
        # Análise do resultado
        if response.status_code == 200:
            print("\n✅ LOGIN REALIZADO COM SUCESSO!")
            return True
        elif response.status_code == 401:
            print("\n❌ ERRO 401 - UNAUTHORIZED")
            print("🔍 Possíveis causas:")
            print("   1. Credenciais incorretas")
            print("   2. Usuário não encontrado")
            print("   3. Senha não confere")
            print("   4. Middleware bloqueando")
            return False
        elif response.status_code == 404:
            print("\n❌ ERRO 404 - ENDPOINT NÃO ENCONTRADO")
            return False
        elif response.status_code == 500:
            print("\n❌ ERRO 500 - ERRO INTERNO DO SERVIDOR")
            return False
        else:
            print(f"\n⚠️  STATUS INESPERADO: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ERRO DE CONEXÃO: {str(e)}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"\n❌ TIMEOUT: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        return False

def testar_credenciais_alternativas():
    """Testa com diferentes variações das credenciais"""
    
    print("\n🔍 TESTE COM CREDENCIAIS ALTERNATIVAS")
    print("="*50)
    
    url = "https://bigwhale-backend.onrender.com/api/auth/login"
    
    # Variações de credenciais para testar
    credenciais_teste = [
        {
            "email": "luciano.curty@gmail.com",
            "password": "Nautilus2025@",
            "descricao": "Credenciais atuais"
        },
        {
            "email": "luciano.curty@gmail.com", 
            "password": "123456",
            "descricao": "Senha antiga possível"
        },
        {
            "email": "admin@bigwhale.com",
            "password": "admin123",
            "descricao": "Credenciais de admin"
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://bwhale.site"
    }
    
    for i, cred in enumerate(credenciais_teste, 1):
        print(f"\n📋 TESTE {i}: {cred['descricao']}")
        print(f"📧 Email: {cred['email']}")
        print(f"🔑 Senha: {'*' * len(cred['password'])}")
        
        try:
            response = requests.post(
                url,
                json={"email": cred["email"], "password": cred["password"]},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ LOGIN SUCESSO!")
                try:
                    data = response.json()
                    print(f"📄 Usuário: {data.get('user', {}).get('name', 'N/A')}")
                except:
                    pass
            elif response.status_code == 401:
                print("❌ 401 - Credenciais inválidas")
            else:
                print(f"⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

def verificar_usuario_banco_local():
    """Verifica se o usuário existe no banco local"""
    
    print("\n🔍 VERIFICAÇÃO NO BANCO LOCAL")
    print("="*40)
    
    import sqlite3
    
    banco_paths = [
        "C:\\Nautilus Aut\\RetesteProjeto\\backend\\instance\\site.db",
        "C:\\Nautilus Aut\\RetesteProjeto\\instance\\site.db"
    ]
    
    for banco_path in banco_paths:
        try:
            print(f"\n📂 Verificando: {banco_path}")
            
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            
            # Buscar usuário
            cursor.execute(
                "SELECT id, name, email, password_hash, is_active FROM users WHERE email = ?",
                ("luciano.curty@gmail.com",)
            )
            
            user = cursor.fetchone()
            
            if user:
                print(f"✅ Usuário encontrado:")
                print(f"   ID: {user[0]}")
                print(f"   Nome: {user[1]}")
                print(f"   Email: {user[2]}")
                print(f"   Hash da senha: {user[3][:20]}...")
                print(f"   Ativo: {user[4]}")
                
                # Testar senha
                senha_teste = "Nautilus2025@"
                if check_password_hash(user[3], senha_teste):
                    print(f"✅ Senha '{senha_teste}' confere!")
                else:
                    print(f"❌ Senha '{senha_teste}' NÃO confere")
                    
            else:
                print("❌ Usuário não encontrado")
                
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao acessar {banco_path}: {str(e)}")

def main():
    print("🔧 DIAGNÓSTICO COMPLETO - ERRO 401 LOGIN")
    print("="*60)
    print(f"🕐 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Executar testes
    sucesso_producao = testar_login_producao()
    testar_credenciais_alternativas()
    verificar_usuario_banco_local()
    
    # Resumo final
    print("\n🎯 RESUMO FINAL")
    print("="*30)
    
    if sucesso_producao:
        print("✅ Login em produção: SUCESSO")
    else:
        print("❌ Login em produção: FALHOU")
        print("\n🔧 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("   1. Verificar logs do servidor de produção")
        print("   2. Confirmar se o usuário existe no banco de produção")
        print("   3. Verificar configuração do middleware")
        print("   4. Testar com outras credenciais conhecidas")
        print("   5. Verificar se há diferenças entre local e produção")

if __name__ == "__main__":
    main()