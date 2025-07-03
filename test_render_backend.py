#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a conectividade com o backend no Render
"""

import requests
import json
from datetime import datetime

def test_backend_connectivity():
    """Testa a conectividade com o backend no Render"""
    
    base_url = "https://bigwhale-backend-o.onrender.com"
    
    endpoints = [
        "/api/health",
        "/api/test",
        "/api/auth/login"
    ]
    
    print(f"🔍 Testando conectividade com o backend Render...")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL Base: {base_url}")
    print("=" * 60)
    
    results = {}
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🧪 Testando: {endpoint}")
        
        try:
            if endpoint == "/api/auth/login":
                # Teste de login com credenciais de admin
                payload = {
                    "email": "admin@bigwhale.com",
                    "password": "admin123"
                }
                response = requests.post(url, json=payload, timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ⏱️  Tempo de resposta: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"   📄 Resposta (texto): {response.text[:200]}...")
            else:
                print(f"   ❌ Erro: {response.text[:200]}...")
            
            results[endpoint] = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200
            }
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT - Servidor não respondeu em 30s")
            results[endpoint] = {"error": "timeout", "success": False}
            
        except requests.exceptions.ConnectionError:
            print(f"   🔌 ERRO DE CONEXÃO - Servidor inacessível")
            results[endpoint] = {"error": "connection_error", "success": False}
            
        except Exception as e:
            print(f"   💥 ERRO: {str(e)}")
            results[endpoint] = {"error": str(e), "success": False}
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    
    all_success = True
    for endpoint, result in results.items():
        status = "✅ OK" if result.get("success") else "❌ FALHOU"
        print(f"   {endpoint}: {status}")
        if not result.get("success"):
            all_success = False
    
    if all_success:
        print("\n🎉 BACKEND ESTÁ FUNCIONANDO! O Render acordou com sucesso.")
        print("💡 Você pode usar o frontend normalmente agora.")
    else:
        print("\n😴 BACKEND AINDA ESTÁ DORMINDO ou com problemas.")
        print("💡 Soluções:")
        print("   1. Aguarde alguns minutos e teste novamente")
        print("   2. Use o backend local como alternativa")
        print("   3. Execute este script novamente em alguns minutos")
    
    return results

if __name__ == "__main__":
    test_backend_connectivity()