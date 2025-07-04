#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o backend localmente após as correções
"""

import requests
import json
import time

def test_backend():
    """Testa os endpoints principais do backend"""
    base_url = "http://localhost:5000"
    
    print("=== TESTE DO BACKEND LOCAL ===")
    print(f"URL Base: {base_url}")
    print()
    
    # Teste 1: Health Check
    print("1. Testando Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Resposta: {json.dumps(data, indent=2)}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro de conexão: {str(e)}")
    
    print()
    
    # Teste 2: Login com credenciais de admin
    print("2. Testando Login...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Login bem-sucedido: {data.get('message', 'N/A')}")
            print(f"   User ID: {data.get('user_id', 'N/A')}")
        else:
            print(f"   Erro no login: {response.text}")
            
    except Exception as e:
        print(f"   Erro de conexão: {str(e)}")
    
    print()
    
    # Teste 3: Verificação de Sessão
    print("3. Testando Verificação de Sessão...")
    try:
        response = requests.get(f"{base_url}/api/auth/session", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Sessão válida: {data.get('valid', False)}")
        else:
            print(f"   Erro: {response.text}")
    except Exception as e:
        print(f"   Erro de conexão: {str(e)}")
    
    print()
    print("=== FIM DOS TESTES ===")

if __name__ == "__main__":
    test_backend()