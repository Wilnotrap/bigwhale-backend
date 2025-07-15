#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar dados das APIs no PostgreSQL (Render)
"""

import os
import requests
import json
from datetime import datetime

def verificar_via_api():
    """
    Verifica dados via endpoint da API já deployada
    """
    print("🔍 VERIFICANDO POSTGRESQL VIA API")
    print("=" * 60)
    
    base_url = "https://bigwhale-backend.onrender.com"
    
    try:
        # 1. Verificar saúde do sistema
        print("1️⃣ Verificando saúde do backend...")
        health_response = requests.get(f"{base_url}/api/health", timeout=10)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Backend online - {health_data.get('users_count', 0)} usuários")
            print(f"🗄️ Banco: {health_data.get('database_type', 'N/A')}")
            print(f"📅 Última verificação: {health_data.get('timestamp', 'N/A')}")
        else:
            print(f"❌ Backend com problemas: {health_response.status_code}")
            return
        
        print("\n" + "=" * 60)
        
        # 2. Tentar fazer login para acessar dados protegidos
        print("2️⃣ Testando fluxo de login...")
        
        session = requests.Session()
        
        # Teste com usuário conhecido (se existe)
        login_data = {
            "email": "luciano.curty@gmail.com",
            "password": "Nautilus2025@"
        }
        
        login_response = session.post(
            f"{base_url}/api/auth/login", 
            json=login_data, 
            timeout=15
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"✅ Login realizado: {login_result.get('message', 'N/A')}")
            
            # 3. Verificar perfil do usuário logado
            print("\n3️⃣ Verificando perfil do usuário...")
            profile_response = session.get(f"{base_url}/api/auth/profile", timeout=10)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                user = profile_data.get('user', {})
                
                print(f"👤 Usuário: {user.get('full_name', 'N/A')}")
                print(f"📧 Email: {user.get('email', 'N/A')}")
                print(f"🆔 ID: {user.get('id', 'N/A')}")
                
                # Verificar status da API
                api_configured = user.get('api_configured', False)
                has_api_key = bool(user.get('bitget_api_key', ''))
                has_api_secret = bool(user.get('bitget_api_secret', ''))
                has_passphrase = bool(user.get('bitget_passphrase', ''))
                
                print(f"🔑 API Configurada: {'✅' if api_configured else '❌'}")
                print(f"🔑 Tem API Key: {'✅' if has_api_key else '❌'}")
                print(f"🔑 Tem API Secret: {'✅' if has_api_secret else '❌'}")
                print(f"🔑 Tem Passphrase: {'✅' if has_passphrase else '❌'}")
                
                if has_api_key:
                    print(f"📝 API Key: {user.get('bitget_api_key', '')[:20]}...")
                
                # 4. Testar botão "Conectar API"
                print("\n4️⃣ Testando botão 'Conectar API'...")
                connect_response = session.post(f"{base_url}/api/dashboard/reconnect-api", timeout=15)
                
                print(f"📊 Status: {connect_response.status_code}")
                if connect_response.status_code == 200:
                    connect_data = connect_response.json()
                    print(f"✅ Conexão: {connect_data.get('success', False)}")
                    print(f"📝 Mensagem: {connect_data.get('message', 'N/A')}")
                else:
                    try:
                        error_data = connect_response.json()
                        print(f"❌ Erro: {error_data.get('message', 'N/A')}")
                        print(f"🔧 Código: {error_data.get('code', 'N/A')}")
                    except:
                        print(f"❌ Erro HTTP: {connect_response.text[:200]}")
                
            else:
                print(f"❌ Erro ao acessar perfil: {profile_response.status_code}")
                
        else:
            print(f"❌ Falha no login: {login_response.status_code}")
            try:
                error_data = login_response.json()
                print(f"Erro: {error_data.get('message', 'N/A')}")
            except:
                print("Erro desconhecido no login")
                
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def gerar_relatorio():
    """
    Gera relatório detalhado do diagnóstico
    """
    print("\n" + "=" * 60)
    print("📋 DIAGNÓSTICO COMPLETO")
    print("=" * 60)
    
    print("""
🔍 PROBLEMAS IDENTIFICADOS:

1. **PERFIL NÃO CARREGA CREDENCIAIS**
   - Dados salvos no cadastro mas não aparecem no perfil
   - Usuário tem que digitar novamente
   
2. **BOTÃO "CONECTAR API" FALHA**
   - Erro 400 (Bad Request)
   - Não consegue buscar credenciais do banco

3. **MIGRAÇÃO PostgreSQL**
   - Possível problema na query/descriptografia
   - Conexão ou estrutura da tabela

🛠️ SOLUÇÕES RECOMENDADAS:

1. **Verificar endpoint /profile**
   - Corrigir busca das credenciais descriptografadas
   - Garantir que retorna os dados corretos

2. **Corrigir botão "Conectar API"**
   - Endpoint /reconnect-api precisa funcionar
   - Melhorar tratamento de erros

3. **Validar PostgreSQL**
   - Confirmar que dados estão sendo salvos
   - Testar descriptografia das credenciais

4. **Frontend**
   - Garantir que está recebendo dados do backend
   - Exibir credenciais no formulário do perfil
""")

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO NAUTILUS - POSTGRESQL")
    print("Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print()
    
    verificar_via_api()
    gerar_relatorio() 