#!/usr/bin/env python3
"""
Teste simples do webhook do Stripe
"""

import requests
import json

def test_webhook_endpoints():
    """
    Testa os endpoints do webhook
    """
    # URL base do seu backend no Render
    base_url = "https://bigwhale-backend.onrender.com"  # Substitua pela sua URL
    
    endpoints = [
        "/api/webhook/test",
        "/api/webhook/status", 
        "/api/health"
    ]
    
    print("🧪 Testando endpoints do webhook...")
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n📡 Testando: {url}")
            
            response = requests.get(url, timeout=10)
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
        except Exception as e:
            print(f"❌ Erro ao testar {endpoint}: {str(e)}")
    
    print("\n🏁 Teste concluído!")

def test_webhook_post():
    """
    Simula um webhook do Stripe
    """
    base_url = "https://bigwhale-backend.onrender.com"  # Substitua pela sua URL
    
    # Dados simulados do Stripe
    fake_stripe_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123456",
                "customer_details": {
                    "email": "teste@webhook.com"
                },
                "amount_total": 5000
            }
        }
    }
    
    try:
        url = f"{base_url}/api/webhook/stripe"
        print(f"\n📡 Testando POST no webhook: {url}")
        
        response = requests.post(
            url,
            json=fake_stripe_event,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "t=123456,v1=fake_signature"
            },
            timeout=10
        )
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Erro ao testar webhook POST: {str(e)}")

if __name__ == "__main__":
    test_webhook_endpoints()
    test_webhook_post() 