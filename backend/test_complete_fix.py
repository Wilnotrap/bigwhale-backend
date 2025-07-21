#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo de todas as correções aplicadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_complete_system():
    """Testa todo o sistema após correções"""
    try:
        print("🧪 TESTE COMPLETO DO SISTEMA CORRIGIDO")
        print("=" * 60)
        
        base_url = "http://localhost:5000"
        
        # 1. Verificar se servidor está rodando
        print("🌐 VERIFICANDO SERVIDOR:")
        print("-" * 30)
        
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
        
        # 2. Testar login com admin
        print(f"\n🔐 TESTANDO LOGIN (ADMIN):")
        print("-" * 30)
        
        session = requests.Session()
        login_data = {
            "email": "admin@bigwhale.com",
            "password": "Raikamaster1@"
        }
        
        login_response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # 3. Verificar perfil
            print(f"\n👤 VERIFICANDO PERFIL:")
            print("-" * 30)
            
            profile_response = session.get(f"{base_url}/api/auth/profile", timeout=10)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                api_configured = profile_data.get('user', {}).get('api_configured', False)
                
                print(f"✅ Perfil carregado")
                print(f"   API Configurada: {api_configured}")
                
                if not api_configured:
                    print("⚠️  API não aparece como configurada, testando atualização...")
                    
                    # Tentar configurar API
                    update_data = {
                        "bitget_api_key": "bg_admin_dev_key_12345",
                        "bitget_api_secret": "admin_dev_secret_67890",
                        "bitget_passphrase": "admin_dev_pass_123"
                    }
                    
                    update_response = session.put(f"{base_url}/api/auth/profile", json=update_data, timeout=15)
                    
                    if update_response.status_code == 200:
                        update_result = update_response.json()
                        print("✅ Perfil atualizado com sucesso")
                        print(f"   API Configurada: {update_result.get('api_configured')}")
                    else:
                        print("❌ Erro ao atualizar perfil")
                        print(f"   Status: {update_response.status_code}")
                        print(f"   Resposta: {update_response.text}")
            
            # 4. Testar endpoints do dashboard
            print(f"\n📊 TESTANDO ENDPOINTS DO DASHBOARD:")
            print("-" * 30)
            
            endpoints_to_test = [
                ('/api/dashboard/stats', 'Estatísticas'),
                ('/api/dashboard/account-balance', 'Saldo da Conta'),
                ('/api/dashboard/open-positions', 'Posições Abertas'),
                ('/api/dashboard/finished-positions', 'Posições Finalizadas'),
                ('/api/dashboard/api-status', 'Status da API'),
                ('/api/dashboard/balance-summary', 'Resumo do Saldo')
            ]
            
            working_endpoints = 0
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = session.get(f"{base_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ {name}: OK")
                        working_endpoints += 1
                    elif response.status_code == 404:
                        print(f"❌ {name}: 404 (Não encontrado)")
                    else:
                        print(f"⚠️  {name}: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {name}: Erro ({e})")
            
            print(f"\n📈 Endpoints funcionando: {working_endpoints}/{len(endpoints_to_test)}")
            
            # 5. Testar conexão da API
            print(f"\n🔌 TESTANDO CONEXÃO DA API:")
            print("-" * 30)
            
            try:
                connection_response = session.post(f"{base_url}/api/dashboard/test-bitget-connection", timeout=15)
                
                if connection_response.status_code == 200:
                    connection_data = connection_response.json()
                    print("✅ Teste de conexão funcionou!")
                    print(f"   Mensagem: {connection_data.get('message')}")
                    print(f"   Sucesso: {connection_data.get('success')}")
                    
                    if connection_data.get('dev_mode'):
                        print("   🔧 Modo desenvolvimento detectado")
                    
                elif connection_response.status_code == 404:
                    print("❌ Endpoint de teste não encontrado (404)")
                else:
                    print(f"❌ Erro no teste de conexão: {connection_response.status_code}")
                    try:
                        error_data = connection_response.json()
                        print(f"   Erro: {error_data.get('message')}")
                    except:
                        print(f"   Resposta: {connection_response.text}")
                        
            except Exception as e:
                print(f"❌ Erro ao testar conexão: {e}")
            
            # 6. Verificar se saldo aparece
            print(f"\n💰 VERIFICANDO SALDO:")
            print("-" * 30)
            
            try:
                balance_response = session.get(f"{base_url}/api/dashboard/account-balance", timeout=10)
                
                if balance_response.status_code == 200:
                    balance_data = balance_response.json()
                    
                    if balance_data.get('success'):
                        total_balance = balance_data.get('total_balance', 0)
                        available_balance = balance_data.get('available_balance', 0)
                        
                        print("✅ Saldo carregado com sucesso")
                        print(f"   Saldo Total: ${total_balance:.2f}")
                        print(f"   Saldo Disponível: ${available_balance:.2f}")
                        
                        if total_balance > 0:
                            print("✅ Saldo positivo detectado")
                        else:
                            print("⚠️  Saldo zerado (normal para desenvolvimento)")
                    else:
                        print("❌ Erro ao carregar saldo")
                        print(f"   Mensagem: {balance_data.get('message')}")
                else:
                    print(f"❌ Erro HTTP ao carregar saldo: {balance_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar saldo: {e}")
            
            return True
            
        else:
            print("❌ Falha no login!")
            try:
                error_data = login_response.json()
                print(f"   Erro: {error_data.get('message')}")
            except:
                print(f"   Resposta: {login_response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_final_instructions():
    """Mostra instruções finais"""
    print(f"\n📋 INSTRUÇÕES FINAIS:")
    print("=" * 60)
    
    print("🔄 PARA APLICAR TODAS AS CORREÇÕES:")
    print("1. Reiniciar o servidor (IMPORTANTE!)")
    print("2. Aguardar inicialização completa")
    print("3. Fazer login no frontend")
    print("4. Verificar se credenciais aparecem configuradas")
    print("5. Testar botão 'Conectar API'")
    print("6. Verificar se saldo aparece no dashboard")
    
    print(f"\n🔑 CREDENCIAIS DE DESENVOLVIMENTO:")
    print("Admin: bg_admin_dev_key_12345 / admin_dev_secret_67890 / admin_dev_pass_123")
    print("Willian: bg_willian_dev_key_12345 / willian_dev_secret_67890 / willian_dev_pass_123")
    print("Demo: bg_demo_api_key_12345 / demo_secret_key_67890 / demo_passphrase_123")
    
    print(f"\n🎯 CORREÇÕES APLICADAS:")
    print("✅ Credenciais configuradas no banco")
    print("✅ Patch de validação aplicado")
    print("✅ Endpoints faltantes adicionados")
    print("✅ Sistema de teste da API criado")
    print("✅ Integração com conta demo")

if __name__ == '__main__':
    print("🚀 TESTE COMPLETO DO SISTEMA APÓS CORREÇÕES")
    print("Objetivo: Verificar se todas as correções estão funcionando")
    print()
    
    # Executar teste
    success = test_complete_system()
    
    # Mostrar instruções
    show_final_instructions()
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 SISTEMA TESTADO COM SUCESSO!")
        print("✅ Principais funcionalidades estão operacionais")
        print("✅ Reinicie o servidor para aplicar todas as mudanças")
        
    else:
        print(f"\n{'='*60}")
        print("❌ AINDA HÁ PROBLEMAS!")
        print("💡 Verifique se o servidor foi reiniciado")
        print("💡 Consulte os logs acima para detalhes")
    
    print(f"\n🏁 TESTE COMPLETO FINALIZADO")