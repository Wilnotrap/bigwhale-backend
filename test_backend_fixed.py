# test_backend_fixed.py - Teste do backend corrigido
import requests
import json

def test_backend_fixed():
    """Testa o backend corrigido localmente"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Testando backend corrigido...\n")
    
    # 1. Testar health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"✅ Health Check: {response.status_code}")
        health_data = response.json()
        print(f"   Users count: {health_data.get('users_count', 'N/A')}")
        print(f"   Status: {health_data.get('status', 'N/A')}\n")
    except Exception as e:
        print(f"❌ Health Check falhou: {e}\n")
    
    # 2. Testar login com credenciais admin
    login_tests = [
        {
            "name": "Admin BigWhale",
            "email": "admin@bigwhale.com",
            "password": "Raikamaster1@"
        },
        {
            "name": "Willian Admin", 
            "email": "willian@lexxusadm.com.br",
            "password": "Bigwhale202021@"
        }
    ]
    
    for test in login_tests:
        print(f"🔐 Testando login: {test['name']}")
        try:
            payload = {
                "email": test["email"],
                "password": test["password"]
            }
            
            response = requests.post(
                f"{base_url}/api/auth/login",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                login_data = response.json()
                print(f"   ✅ Login bem-sucedido!")
                print(f"   User: {login_data.get('user', {}).get('email', 'N/A')}")
                print(f"   Message: {login_data.get('message', 'N/A')}")
            else:
                print(f"   ❌ Login falhou")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('message', 'Erro desconhecido')}")
                except:
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")
        
        print()
    
    print("\n🏁 Teste do backend corrigido concluído.")

if __name__ == '__main__':
    test_backend_fixed()