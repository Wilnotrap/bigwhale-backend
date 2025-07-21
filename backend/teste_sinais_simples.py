#!/usr/bin/env python3
"""
Teste simples para verificar sinais
"""

import requests
import json

def teste_sinais():
    """Testa se há sinais sendo sincronizados"""
    
    print("🧪 TESTE DE SINAIS")
    print("=" * 30)
    
    try:
        # Testar endpoint de operações ativas
        response = requests.get('http://localhost:5000/api/dashboard/nautilus-operacional/active-operations')
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint funcionando!")
            print(f"📈 Total de operações: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"📋 Primeira operação: {data[0].get('symbol', 'N/A')}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    teste_sinais() 