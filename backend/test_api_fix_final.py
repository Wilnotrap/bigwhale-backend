#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final da correção das credenciais da API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_api_fix_for_all_users():
    """Testa a correção para todos os usuários"""
    try:
        print("🧪 TESTE FINAL DA CORREÇÃO DAS CREDENCIAIS")
        print("=" * 60)
        
        base_url = "http://localhost:5000"
        
        # Verificar se servidor está rodando
        try:
            health_response = requests.get(f"{base_url}/api/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ Servidor está rodando")
            else:
                print(f"⚠️  Servidor respondeu com status: {health_response.status_code}")
        except Exception as e:
            print(f"❌ Servidor não está rodando: {e}")
            print("💡 Inicie o servidor com: .venv\\Scripts\\python.exe app.py")
            return False
        
        # Credenciais de teste para cada usuário
        test_users = [
            {
                "name": "Admin Principal",
                "email": "admin@bigwhale.com",
                "password": "Raikamaster1@",
                "api_key": "bg_admin_dev_key_12345",
                "secret": "admin_dev_secret_67890",
                "passphrase": "admin_dev_pass_123"
            },
            {
                "name": "Willian Admin",
                "email": "willian@lexxusadm.com.br", 
                "password": "Bigwhale202021@",
                "api_key": "bg_willian_dev_key_12345",
                "secret": "willian_dev_secret_67890",
                "passphrase": "willian_dev_pass_123"
            },
            {
                "name": "Conta Demo",
                "email": "financeiro@lexxusadm.com.br",
                "password": "FinanceiroDemo2025@",
                "api_key": "bg_demo_api_key_12345",
                "secret": "demo_secret_key_67890",
                "passphrase": "demo_passphrase_123"
            }
        ]
        
        successful_tests = 0
        
        for user in test_users:
            print(f"\n🔍 TESTANDO: {user['name']} ({user['email']})")
            print("-" * 50)
            
            session = requests.Session()
            
            # 1. Teste de login
            login_data = {
                "email": user["email"],
                "password": user["password"]
            }
            
            try:
                login_response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
                
                if login_response.status_code == 200:
                    print("✅ Login realizado com sucesso")
                    
                    # 2. Verificar se credenciais já estão configuradas
                    profile_response = session.get(f"{base_url}/api/auth/profile", timeout=10)
                    
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        
                        if profile_data.get('user', {}).get('api_configured'):
                            print("✅ Credenciais já estão configuradas no perfil")
                        else:
                            print("⚠️  Credenciais não aparecem como configuradas")
                    
                    # 3. Testar atualização do perfil (mesmo que já configurado)
                    update_data = {
                        "bitget_api_key": user["api_key"],
                        "bitget_api_secret": user["secret"],
                        "bitget_passphrase": user["passphrase"]
                    }
                    
                    update_response = session.put(f"{base_url}/api/auth/profile", json=update_data, timeout=15)
                    
                    print(f"Status da atualização: {update_response.status_code}")
                    
                    if update_response.status_code == 200:
                        response_data = update_response.json()
                        print("✅ Atualização do perfil funcionou!")
                        print(f"   Mensagem: {response_data.get('message')}")
                        print(f"   API Configurada: {response_data.get('api_configured')}")
                        print(f"   Sucesso: {response_data.get('success')}")
                        
                        # 4. Verificar se realmente salvou
                        verify_response = session.get(f"{base_url}/api/auth/profile", timeout=10)
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            api_configured = verify_data.get('user', {}).get('api_configured', False)
                            
                            if api_configured:
                                print("✅ Verificação: Credenciais estão salvas e configuradas")
                                successful_tests += 1
                            else:
                                print("❌ Verificação: Credenciais NÃO estão configuradas")
                        else:
                            print("❌ Erro ao verificar perfil após atualização")
                    
                    else:
                        print("❌ Erro na atualização do perfil!")
                        try:
                            error_data = update_response.json()
                            print(f"   Erro: {error_data.get('message')}")
                        except:
                            print(f"   Resposta: {update_response.text}")
                
                else:
                    print("❌ Falha no login!")
                    try:
                        error_data = login_response.json()
                        print(f"   Erro: {error_data.get('message')}")
                    except:
                        print(f"   Resposta: {login_response.text}")
            
            except Exception as e:
                print(f"❌ Erro no teste: {e}")
        
        # Resultado final
        print(f"\n{'='*60}")
        print(f"📊 RESULTADO FINAL DO TESTE:")
        print(f"✅ Testes bem-sucedidos: {successful_tests}/{len(test_users)}")
        
        if successful_tests == len(test_users):
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema de credenciais da API está funcionando")
            print("✅ Problema resolvido para todos os usuários")
        elif successful_tests > 0:
            print("⚠️  ALGUNS TESTES PASSARAM")
            print("💡 Verifique os usuários que falharam")
        else:
            print("❌ TODOS OS TESTES FALHARAM")
            print("💡 Verifique se o servidor foi reiniciado")
            print("💡 Verifique se o patch foi aplicado corretamente")
        
        return successful_tests == len(test_users)
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_credentials_reference():
    """Mostra referência das credenciais"""
    print(f"\n📋 REFERÊNCIA DAS CREDENCIAIS DE DESENVOLVIMENTO:")
    print("=" * 60)
    
    credentials = [
        ("Admin Principal", "admin@bigwhale.com", "bg_admin_dev_key_12345", "admin_dev_secret_67890", "admin_dev_pass_123"),
        ("Willian Admin", "willian@lexxusadm.com.br", "bg_willian_dev_key_12345", "willian_dev_secret_67890", "willian_dev_pass_123"),
        ("Conta Demo", "financeiro@lexxusadm.com.br", "bg_demo_api_key_12345", "demo_secret_key_67890", "demo_passphrase_123")
    ]
    
    for name, email, api_key, secret, passphrase in credentials:
        print(f"\n🔑 {name} ({email}):")
        print(f"   API Key: {api_key}")
        print(f"   Secret: {secret}")
        print(f"   Passphrase: {passphrase}")

if __name__ == '__main__':
    print("🚀 TESTE FINAL DA CORREÇÃO DAS CREDENCIAIS DA API")
    print("Objetivo: Verificar se o problema foi resolvido para todos os usuários")
    print()
    
    # Executar teste
    success = test_api_fix_for_all_users()
    
    # Mostrar credenciais de referência
    show_credentials_reference()
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 CORREÇÃO CONFIRMADA!")
        print("✅ Sistema de credenciais da API está funcionando")
        print("✅ Todos os usuários podem configurar credenciais")
        print("✅ Problema resolvido definitivamente")
        
        print(f"\n💡 INSTRUÇÕES PARA USO:")
        print("1. Faça login com qualquer usuário")
        print("2. Vá para Perfil/Configurações")
        print("3. Use as credenciais de desenvolvimento correspondentes")
        print("4. Clique em 'Salvar' - deve funcionar")
        print("5. Teste 'Conectar API' - deve funcionar")
        
    else:
        print(f"\n{'='*60}")
        print("❌ AINDA HÁ PROBLEMAS!")
        print("💡 Verifique se o servidor foi reiniciado")
        print("💡 Verifique se o patch foi aplicado")
        print("💡 Consulte os logs acima para detalhes")
    
    print(f"\n🏁 TESTE FINALIZADO")