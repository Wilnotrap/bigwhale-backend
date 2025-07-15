#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuário de teste e validar fluxo completo no PostgreSQL
"""

import requests
import json
import time
from datetime import datetime

def criar_usuario_teste():
    """
    Cria usuário de teste via API e valida todo o fluxo
    """
    print("🚀 CRIANDO USUÁRIO DE TESTE - POSTGRESQL")
    print("=" * 60)
    
    base_url = "https://bigwhale-backend.onrender.com"
    
    # Dados do usuário de teste
    timestamp = int(time.time())
    user_data = {
        "full_name": "Teste Postgresql",
        "email": f"teste.postgresql.{timestamp}@exemplo.com",
        "password": "TestePostgres123@",
        "bitget_api_key": "bg_test_postgresql_api_key_123456789012345",
        "bitget_api_secret": "bg_test_postgresql_secret_abcdefghijklmnopqrstuvwxyz123456789012345",
        "bitget_passphrase": "bg_test_postgresql_passphrase_123",
        "invite_code": "Bigwhale81#",
        "paid_user": False
    }
    
    print(f"📧 Email: {user_data['email']}")
    print(f"👤 Nome: {user_data['full_name']}")
    print(f"🔑 Senha: {user_data['password']}")
    print(f"🧪 API Key: {user_data['bitget_api_key'][:30]}...")
    
    try:
        # 1. Fazer cadastro
        print("\n1️⃣ FAZENDO CADASTRO...")
        register_response = requests.post(
            f"{base_url}/api/auth/register",
            json=user_data,
            timeout=30
        )
        
        print(f"📊 Status: {register_response.status_code}")
        
        if register_response.status_code == 200 or register_response.status_code == 201:
            register_data = register_response.json()
            print(f"✅ Cadastro realizado: {register_data.get('message', 'N/A')}")
            
            # 2. Fazer login
            print("\n2️⃣ FAZENDO LOGIN...")
            session = requests.Session()
            
            login_data = {
                "email": user_data['email'],
                "password": user_data['password']
            }
            
            login_response = session.post(
                f"{base_url}/api/auth/login",
                json=login_data,
                timeout=15
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print(f"✅ Login realizado: {login_result.get('message', 'N/A')}")
                
                # 3. Verificar perfil
                print("\n3️⃣ VERIFICANDO PERFIL...")
                profile_response = session.get(f"{base_url}/api/auth/profile", timeout=10)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    user = profile_data.get('user', {})
                    
                    print(f"👤 Usuário: {user.get('full_name', 'N/A')}")
                    print(f"🆔 ID: {user.get('id', 'N/A')}")
                    
                    # Verificar se as credenciais estão no perfil
                    api_configured = user.get('api_configured', False)
                    has_api_key = bool(user.get('bitget_api_key', ''))
                    has_api_secret = bool(user.get('bitget_api_secret', ''))
                    has_passphrase = bool(user.get('bitget_passphrase', ''))
                    
                    print(f"🔑 API Configurada: {'✅' if api_configured else '❌'}")
                    print(f"🔑 Tem API Key: {'✅' if has_api_key else '❌'}")
                    print(f"🔑 Tem API Secret: {'✅' if has_api_secret else '❌'}")
                    print(f"🔑 Tem Passphrase: {'✅' if has_passphrase else '❌'}")
                    
                    if has_api_key:
                        print(f"📝 API Key no perfil: {user.get('bitget_api_key', '')[:30]}...")
                    
                    # 4. Testar botão "Conectar API"
                    print("\n4️⃣ TESTANDO BOTÃO 'CONECTAR API'...")
                    connect_response = session.post(f"{base_url}/api/dashboard/reconnect-api", timeout=15)
                    
                    print(f"📊 Status: {connect_response.status_code}")
                    if connect_response.status_code == 200:
                        connect_data = connect_response.json()
                        print(f"✅ Sucesso: {connect_data.get('success', False)}")
                        print(f"📝 Mensagem: {connect_data.get('message', 'N/A')}")
                        
                        if connect_data.get('success'):
                            print("🎉 BOTÃO 'CONECTAR API' FUNCIONANDO!")
                        else:
                            print("❌ Botão falhou mesmo com status 200")
                    else:
                        try:
                            error_data = connect_response.json()
                            print(f"❌ Erro: {error_data.get('message', 'N/A')}")
                            print(f"🔧 Código: {error_data.get('code', 'N/A')}")
                        except:
                            print(f"❌ Erro HTTP: {connect_response.text[:200]}")
                    
                    # 5. Resumo final
                    print("\n" + "=" * 60)
                    print("📋 RESUMO DO TESTE")
                    print("=" * 60)
                    
                    tests_passed = 0
                    total_tests = 4
                    
                    print("✅ Cadastro: OK")
                    tests_passed += 1
                    
                    print("✅ Login: OK")
                    tests_passed += 1
                    
                    if api_configured and has_api_key and has_api_secret and has_passphrase:
                        print("✅ Perfil com credenciais: OK")
                        tests_passed += 1
                    else:
                        print("❌ Perfil com credenciais: FALHOU")
                    
                    if connect_response.status_code == 200:
                        connect_data = connect_response.json()
                        if connect_data.get('success'):
                            print("✅ Botão 'Conectar API': OK")
                            tests_passed += 1
                        else:
                            print("❌ Botão 'Conectar API': FALHOU")
                    else:
                        print("❌ Botão 'Conectar API': FALHOU")
                    
                    print(f"\n🎯 RESULTADO: {tests_passed}/{total_tests} testes passaram")
                    
                    if tests_passed == total_tests:
                        print("🎉 TODOS OS PROBLEMAS RESOLVIDOS!")
                        print("✅ O fluxo está funcionando corretamente")
                        print("✅ Credenciais aparecem no perfil")
                        print("✅ Botão 'Conectar API' funciona")
                        return True
                    else:
                        print("⚠️ Alguns problemas ainda precisam ser resolvidos")
                        return False
                    
                else:
                    print(f"❌ Erro ao acessar perfil: {profile_response.status_code}")
                    return False
                    
            else:
                print(f"❌ Falha no login: {login_response.status_code}")
                return False
                
        else:
            print(f"❌ Falha no cadastro: {register_response.status_code}")
            try:
                error_data = register_response.json()
                print(f"Erro: {error_data.get('message', 'N/A')}")
            except:
                print("Erro desconhecido no cadastro")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def gerar_instrucoes_deploy():
    """
    Gera instruções para deploy das correções
    """
    print("\n" + "=" * 60)
    print("🚀 INSTRUÇÕES PARA DEPLOY")
    print("=" * 60)
    
    print("""
📁 ARQUIVOS ALTERADOS:
   - backend/auth/routes.py (endpoint /profile corrigido)
   - backend/api/dashboard.py (endpoint /reconnect-api corrigido)

🔧 CORREÇÕES IMPLEMENTADAS:
   ✅ Endpoint /profile retorna dados no formato correto
   ✅ Credenciais descriptografadas incluídas na resposta
   ✅ Botão "Conectar API" simplificado e corrigido
   ✅ Formato de resposta padronizado

📦 PRÓXIMOS PASSOS:
   1. Fazer commit das alterações
   2. Deploy no Render
   3. Testar com usuários reais
   4. Validar funcionamento completo

💡 COMANDOS:
   git add backend/auth/routes.py backend/api/dashboard.py
   git commit -m "fix: Corrigir perfil e botão Conectar API para PostgreSQL"
   git push origin main

🎯 RESULTADO ESPERADO:
   - Usuário faz cadastro → Credenciais aparecem no perfil automaticamente
   - Botão "Conectar API" funciona sem erros
   - Sistema funciona perfeitamente com PostgreSQL
""")

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DO FLUXO - POSTGRESQL")
    print("Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print()
    
    sucesso = criar_usuario_teste()
    gerar_instrucoes_deploy()
    
    if sucesso:
        print("\n🎉 PROBLEMA RESOLVIDO COM SUCESSO!")
    else:
        print("\n⚠️ Ainda há problemas a resolver...") 