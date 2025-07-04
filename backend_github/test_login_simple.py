#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar o endpoint de login
"""

import requests
import json

def test_backend_health():
    """Testa se o backend está respondendo"""
    print("🔍 Testando saúde do backend...")
    try:
        response = requests.get('https://bigwhale-backend.onrender.com/api/health', timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return False

def test_login_endpoint():
    """Testa o endpoint de login com credenciais válidas"""
    print("\n🔐 Testando endpoint de login...")
    
    # Credenciais de admin conhecidas
    login_data = {
        "email": "admin@bigwhale.com",
        "password": "Raikamaster1@"
    }
    
    try:
        response = requests.post(
            'https://bigwhale-backend.onrender.com/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login bem-sucedido!")
            print(f"Resposta: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Login falhou")
            print(f"Resposta: {response.text}")
            
            # Tentar analisar a resposta como JSON
            try:
                error_data = response.json()
                print(f"Erro estruturado: {json.dumps(error_data, indent=2)}")
            except:
                print("Resposta não é JSON válido")
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_session_endpoint():
    """Testa o endpoint de verificação de sessão"""
    print("\n🔍 Testando endpoint de sessão...")
    try:
        response = requests.get('https://bigwhale-backend.onrender.com/api/auth/session', timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

def main():
    print("🧪 TESTE SIMPLES DO BACKEND BIGWHALE")
    print("=" * 50)
    
    # Teste 1: Health check
    health_ok = test_backend_health()
    
    # Teste 2: Session check
    session_ok = test_session_endpoint()
    
    # Teste 3: Login
    login_ok = test_login_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"Health Check: {'✅ OK' if health_ok else '❌ FALHOU'}")
    print(f"Session Check: {'✅ OK' if session_ok else '❌ FALHOU'}")
    print(f"Login Test: {'✅ OK' if login_ok else '❌ FALHOU'}")
    
    if not health_ok:
        print("\n💡 O backend não está respondendo. Verifique se está rodando.")
    elif not login_ok:
        print("\n💡 O backend está rodando, mas o login está falhando.")
        print("   Isso indica um problema específico no código de login.")
    else:
        print("\n🎉 Todos os testes passaram! O backend está funcionando.")

if __name__ == "__main__":
    main()