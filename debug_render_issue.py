# debug_render_issue.py - Script para debugar problemas específicos do Render
import requests
import json

def test_render_endpoints():
    """Testa endpoints específicos do Render para identificar o problema"""
    base_url = "https://bigwhale-backend.onrender.com"
    
    print("🔍 Debugando problemas do Render...\n")
    
    # 1. Testar health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=30)
        print(f"✅ Health Check: {response.status_code}")
        health_data = response.json()
        print(f"   Users count: {health_data.get('users_count', 'N/A')}")
        print(f"   Environment: {health_data.get('environment', 'N/A')}")
        print(f"   Status: {health_data.get('status', 'N/A')}\n")
    except Exception as e:
        print(f"❌ Health Check falhou: {e}\n")
    
    # 2. Testar endpoint de teste
    try:
        response = requests.get(f"{base_url}/api/test", timeout=30)
        print(f"✅ Test Endpoint: {response.status_code}")
        test_data = response.json()
        print(f"   Message: {test_data.get('message', 'N/A')}")
        print(f"   Environment: {test_data.get('environment', 'N/A')}\n")
    except Exception as e:
        print(f"❌ Test Endpoint falhou: {e}\n")
    
    # 3. Testar login com diferentes payloads
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
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                login_data = response.json()
                print(f"   ✅ Login bem-sucedido!")
                print(f"   User: {login_data.get('user', {}).get('email', 'N/A')}")
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
    
    # 4. Testar com payload inválido para ver o comportamento
    print("🧪 Testando payload inválido...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"invalid": "data"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Response: {error_data}")
        except:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n🏁 Debug concluído.")

if __name__ == '__main__':
    test_render_endpoints()