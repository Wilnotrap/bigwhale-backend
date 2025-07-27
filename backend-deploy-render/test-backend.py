#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o backend BigWhale no Render
"""

import requests
import json
from datetime import datetime

# URL do backend no Render
BASE_URL = "https://bigwhale-backend.onrender.com"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Testar um endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🔍 Testando {method} {endpoint}")
    print(f"   URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            print(f"   ❌ Método {method} não suportado")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"   ✅ Sucesso!")
            
            try:
                json_response = response.json()
                print(f"   📄 Resposta: {json.dumps(json_response, indent=2, ensure_ascii=False)}")
            except:
                print(f"   📄 Resposta (texto): {response.text[:200]}...")
            
            return True
        else:
            print(f"   ❌ Falha! Esperado: {expected_status}, Recebido: {response.status_code}")
            print(f"   📄 Erro: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout - O servidor pode estar inicializando (comum no Render gratuito)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Erro de conexão - Verifique se o serviço está rodando")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

def main():
    """Executar todos os testes"""
    print("🚀 BigWhale Backend - Teste Completo")
    print("====================================")
    print(f"🕐 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL Base: {BASE_URL}")
    
    tests_passed = 0
    total_tests = 0
    
    # Teste 1: Rota raiz
    total_tests += 1
    if test_endpoint("GET", "/"):
        tests_passed += 1
    
    # Teste 2: Health check (verificar PostgreSQL)
    total_tests += 1
    print("\n🔍 Verificando configuração do banco de dados...")
    if test_endpoint("GET", "/api/health"):
        tests_passed += 1
    
    # Teste 3: Login com credenciais admin
    total_tests += 1
    login_data = {
        "email": "admin@bigwhale.com",
        "password": "Raikamaster1@"
    }
    if test_endpoint("POST", "/api/auth/login", login_data):
        tests_passed += 1
    
    # Teste 4: Login com credenciais inválidas
    total_tests += 1
    invalid_login = {
        "email": "invalid@test.com",
        "password": "wrongpassword"
    }
    if test_endpoint("POST", "/api/auth/login", invalid_login, expected_status=401):
        tests_passed += 1
    
    # Teste 5: Registro de novo usuário
    total_tests += 1
    register_data = {
        "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com",
        "password": "TestPassword123!",
        "full_name": "Usuário Teste"
    }
    if test_endpoint("POST", "/api/auth/register", register_data, expected_status=201):
        tests_passed += 1
    
    # Resumo dos testes
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    print(f"✅ Testes aprovados: {tests_passed}/{total_tests}")
    print(f"❌ Testes falharam: {total_tests - tests_passed}/{total_tests}")
    print(f"📈 Taxa de sucesso: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✨ Seu backend está funcionando perfeitamente!")
    elif tests_passed >= total_tests * 0.8:
        print("\n⚠️ MAIORIA DOS TESTES PASSOU")
        print("🔧 Alguns endpoints podem precisar de ajustes")
    else:
        print("\n❌ MUITOS TESTES FALHARAM")
        print("🚨 Verifique se o backend foi deployado corretamente")
        print("💡 Dicas:")
        print("   - Aguarde alguns minutos (serviços gratuitos demoram para iniciar)")
        print("   - Verifique os logs no Render Dashboard")
        print("   - Confirme se o push foi feito no GitHub")
    
    print("\n🔗 Links úteis:")
    print(f"   Backend: {BASE_URL}")
    print(f"   Health: {BASE_URL}/api/health")
    print("   Render Dashboard: https://dashboard.render.com")
    print("   GitHub: https://github.com/Wilnotrap/bigwhale-backend")
    
    print(f"\n🕐 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()