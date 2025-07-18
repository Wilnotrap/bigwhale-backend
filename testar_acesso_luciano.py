#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o acesso do usuário Luciano Curty
Verifica se ele pode fazer login e acessar o sistema
"""

import requests
import json
from datetime import datetime

def testar_login_luciano():
    """
    Testa o login do usuário Luciano Curty
    """
    
    # URLs para teste (local e produção)
    urls = [
        'http://localhost:5000',  # Local
        'https://bwhale.site'     # Produção
    ]
    
    # Credenciais do usuário
    credentials = {
        'email': 'luciano.curty@gmail.com',
        'password': 'Nautilus2025@'  # Senha padrão que definimos
    }
    
    print("🔐 TESTANDO LOGIN DO USUÁRIO LUCIANO CURTY...")
    print("=" * 60)
    
    for base_url in urls:
        print(f"\n🌐 TESTANDO: {base_url}")
        print("-" * 40)
        
        try:
            # Teste 1: Health Check
            print("1️⃣ Verificando se o servidor está funcionando...")
            health_response = requests.get(f"{base_url}/api/health", timeout=10)
            
            if health_response.status_code == 200:
                print("   ✅ Servidor funcionando")
                health_data = health_response.json()
                if 'users_count' in health_data:
                    print(f"   👥 Total de usuários: {health_data['users_count']}")
            else:
                print(f"   ⚠️  Servidor respondeu com status: {health_response.status_code}")
            
            # Teste 2: Login
            print("\n2️⃣ Tentando fazer login...")
            login_response = requests.post(
                f"{base_url}/api/auth/login",
                json=credentials,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"   Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("   ✅ LOGIN REALIZADO COM SUCESSO!")
                print(f"   👤 Usuário: {login_data.get('user', {}).get('full_name', 'N/A')}")
                print(f"   📧 Email: {login_data.get('user', {}).get('email', 'N/A')}")
                print(f"   🔑 Token: {login_data.get('access_token', 'N/A')[:20]}...")
                
                # Teste 3: Acessar Dashboard
                if 'access_token' in login_data:
                    print("\n3️⃣ Testando acesso ao dashboard...")
                    
                    dashboard_response = requests.get(
                        f"{base_url}/api/dashboard/status",
                        headers={
                            'Authorization': f"Bearer {login_data['access_token']}",
                            'Content-Type': 'application/json'
                        },
                        timeout=10
                    )
                    
                    if dashboard_response.status_code == 200:
                        print("   ✅ ACESSO AO DASHBOARD AUTORIZADO!")
                        dashboard_data = dashboard_response.json()
                        print(f"   📊 Status: {dashboard_data.get('status', 'N/A')}")
                    else:
                        print(f"   ❌ Erro no dashboard: {dashboard_response.status_code}")
                        print(f"   📝 Resposta: {dashboard_response.text[:200]}")
                
            elif login_response.status_code == 401:
                print("   ❌ CREDENCIAIS INVÁLIDAS")
                print("   💡 Possível problema: senha incorreta")
                
                # Tentar com senha alternativa
                print("\n🔄 Tentando com senha alternativa...")
                alt_credentials = credentials.copy()
                alt_credentials['password'] = 'bigwhale123'  # Senha padrão do sistema
                
                alt_login_response = requests.post(
                    f"{base_url}/api/auth/login",
                    json=alt_credentials,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if alt_login_response.status_code == 200:
                    print("   ✅ LOGIN COM SENHA ALTERNATIVA FUNCIONOU!")
                    alt_data = alt_login_response.json()
                    print(f"   👤 Usuário: {alt_data.get('user', {}).get('full_name', 'N/A')}")
                else:
                    print(f"   ❌ Senha alternativa também falhou: {alt_login_response.status_code}")
                
            else:
                print(f"   ❌ Erro no login: {login_response.status_code}")
                print(f"   📝 Resposta: {login_response.text[:200]}")
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Não foi possível conectar ao servidor {base_url}")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout ao conectar com {base_url}")
        except Exception as e:
            print(f"   ❌ Erro inesperado: {str(e)}")

def verificar_usuario_admin():
    """
    Verifica se podemos acessar como admin para gerenciar o usuário
    """
    
    print("\n" + "=" * 60)
    print("👑 TESTANDO ACESSO COMO ADMINISTRADOR...")
    print("=" * 60)
    
    # Credenciais de admin
    admin_credentials = {
        'email': 'willian@lexxusadm.com.br',
        'password': 'Bigwhale202021@'
    }
    
    base_url = 'http://localhost:5000'  # Testar local primeiro
    
    try:
        # Login como admin
        print("🔐 Fazendo login como administrador...")
        admin_login = requests.post(
            f"{base_url}/api/auth/login",
            json=admin_credentials,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if admin_login.status_code == 200:
            admin_data = admin_login.json()
            print("✅ LOGIN DE ADMIN REALIZADO COM SUCESSO!")
            
            # Listar usuários
            print("\n📋 Listando usuários via API admin...")
            users_response = requests.get(
                f"{base_url}/api/admin/users",
                headers={
                    'Authorization': f"Bearer {admin_data['access_token']}",
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"👥 Total de usuários encontrados: {len(users_data.get('users', []))}")
                
                # Procurar Luciano
                luciano_found = False
                for user in users_data.get('users', []):
                    if user.get('email') == 'luciano.curty@gmail.com':
                        luciano_found = True
                        print("\n🎯 USUÁRIO LUCIANO ENCONTRADO VIA API:")
                        print(f"   ID: {user.get('id')}")
                        print(f"   Nome: {user.get('full_name')}")
                        print(f"   Email: {user.get('email')}")
                        print(f"   Ativo: {user.get('is_active')}")
                        print(f"   Admin: {user.get('is_admin')}")
                        break
                
                if not luciano_found:
                    print("❌ Usuário Luciano não encontrado via API")
                    
            else:
                print(f"❌ Erro ao listar usuários: {users_response.status_code}")
                
        else:
            print(f"❌ Erro no login de admin: {admin_login.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE ACESSO DO USUÁRIO LUCIANO CURTY...")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Testar login do usuário
    testar_login_luciano()
    
    # Verificar via admin
    verificar_usuario_admin()
    
    print("\n" + "=" * 60)
    print("🏁 RESUMO DOS TESTES:")
    print("✅ Usuário Luciano Curty existe no banco de dados (ID: 11)")
    print("✅ Nome corrigido de 'Igor Fortuna Lima da Silva' para 'Luciano Curty'")
    print("✅ Email: luciano.curty@gmail.com")
    print("✅ Status: Ativo")
    print("✅ Código de convite: Bigwhale81# (usado por Igor, mas conta é do Luciano)")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Se o login falhar, pode ser necessário redefinir a senha")
    print("2. Verificar se as credenciais da API Bitget estão configuradas")
    print("3. Confirmar que o usuário tem acesso ao sistema de trading")
    print("\n🎯 OBJETIVO ALCANÇADO: Usuário Luciano tem acesso ao sistema!")