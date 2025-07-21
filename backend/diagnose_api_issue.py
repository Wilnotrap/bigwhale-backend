#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo do problema de configuração da API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
import requests
import json
from datetime import datetime

def diagnose_api_configuration():
    """Diagnostica problemas na configuração da API"""
    try:
        print("🔍 DIAGNÓSTICO DO PROBLEMA DE CONFIGURAÇÃO DA API")
        print("=" * 60)
        
        # 1. Verificar banco de dados local
        print("📁 VERIFICANDO BANCO DE DADOS LOCAL:")
        print("-" * 40)
        
        db_path = os.path.join('backend', 'instance', 'site.db')
        if not os.path.exists(db_path):
            print("❌ Banco de dados local não encontrado!")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todos os usuários e suas configurações de API
        cursor.execute("""
            SELECT id, full_name, email, is_active, 
                   bitget_api_key_encrypted, bitget_api_secret_encrypted, bitget_passphrase_encrypted,
                   operational_balance_usd, nautilus_active
            FROM users 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        
        if users:
            print(f"✅ {len(users)} usuários encontrados:")
            for user in users:
                api_status = "🔑 API OK" if all([user[4], user[5], user[6]]) else "❌ API Não Configurada"
                print(f"   {user[0]}. {user[1]} ({user[2]})")
                print(f"      Status: {'🟢 Ativo' if user[3] else '🔴 Inativo'} | {api_status}")
                print(f"      Saldo: ${user[7] or 0:.2f} | Nautilus: {'🤖 Ativo' if user[8] else '❌ Inativo'}")
                
                # Verificar se as credenciais estão realmente salvas
                if user[4] and user[5] and user[6]:
                    print(f"      🔐 API Key: {len(user[4])} chars")
                    print(f"      🔐 Secret: {len(user[5])} chars") 
                    print(f"      🔐 Passphrase: {len(user[6])} chars")
                else:
                    print(f"      ⚠️  Credenciais faltando:")
                    print(f"         API Key: {'✅' if user[4] else '❌'}")
                    print(f"         Secret: {'✅' if user[5] else '❌'}")
                    print(f"         Passphrase: {'✅' if user[6] else '❌'}")
                print()
        else:
            print("❌ Nenhum usuário encontrado!")
        
        conn.close()
        
        # 2. Testar endpoints da API local
        print("🌐 TESTANDO ENDPOINTS DA API LOCAL:")
        print("-" * 40)
        
        base_url = "http://localhost:5000"
        
        try:
            # Testar health check
            health_response = requests.get(f"{base_url}/api/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ Servidor local está rodando")
            else:
                print(f"⚠️  Servidor respondeu com status: {health_response.status_code}")
        except Exception as e:
            print(f"❌ Servidor local não está rodando: {e}")
            return False
        
        # 3. Simular processo de configuração da API
        print("\n🔧 SIMULANDO PROCESSO DE CONFIGURAÇÃO:")
        print("-" * 40)
        
        # Dados de teste para configuração
        test_credentials = {
            "api_key": "bg_test_api_key_12345",
            "secret_key": "test_secret_key_67890",
            "passphrase": "test_passphrase"
        }
        
        print("📝 Dados de teste preparados:")
        print(f"   API Key: {test_credentials['api_key']}")
        print(f"   Secret: {test_credentials['secret_key']}")
        print(f"   Passphrase: {test_credentials['passphrase']}")
        
        # Tentar fazer login com conta demo para testar
        session = requests.Session()
        
        login_data = {
            "email": "financeiro@lexxusadm.com.br",
            "password": "FinanceiroDemo2025@"
        }
        
        print(f"\n🔐 Fazendo login com conta demo...")
        login_response = session.post(f"{base_url}/api/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # Testar atualização do perfil
            print("\n📝 Testando atualização do perfil...")
            
            profile_data = {
                "full_name": "Conta Demo Financeiro - Teste",
                "bitget_api_key": test_credentials["api_key"],
                "bitget_api_secret": test_credentials["secret_key"],
                "bitget_passphrase": test_credentials["passphrase"]
            }
            
            profile_response = session.put(f"{base_url}/api/auth/profile", json=profile_data)
            
            print(f"Status da atualização: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                response_data = profile_response.json()
                print("✅ Perfil atualizado com sucesso!")
                print(f"   Mensagem: {response_data.get('message')}")
                print(f"   API Configurada: {response_data.get('api_configured')}")
                print(f"   Credenciais Salvas: {response_data.get('credentials_saved')}")
                
                # Verificar se realmente salvou no banco
                print("\n🔍 Verificando se salvou no banco...")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT bitget_api_key_encrypted, bitget_api_secret_encrypted, bitget_passphrase_encrypted
                    FROM users 
                    WHERE email = ?
                """, ("financeiro@lexxusadm.com.br",))
                
                saved_creds = cursor.fetchone()
                if saved_creds and all(saved_creds):
                    print("✅ Credenciais foram salvas no banco!")
                    print(f"   API Key: {len(saved_creds[0])} chars")
                    print(f"   Secret: {len(saved_creds[1])} chars")
                    print(f"   Passphrase: {len(saved_creds[2])} chars")
                else:
                    print("❌ Credenciais NÃO foram salvas no banco!")
                    print(f"   API Key: {'✅' if saved_creds and saved_creds[0] else '❌'}")
                    print(f"   Secret: {'✅' if saved_creds and saved_creds[1] else '❌'}")
                    print(f"   Passphrase: {'✅' if saved_creds and saved_creds[2] else '❌'}")
                
                conn.close()
                
            else:
                print("❌ Erro na atualização do perfil!")
                try:
                    error_data = profile_response.json()
                    print(f"   Erro: {error_data.get('message')}")
                except:
                    print(f"   Resposta: {profile_response.text}")
        
        else:
            print("❌ Falha no login!")
            try:
                error_data = login_response.json()
                print(f"   Erro: {error_data.get('message')}")
            except:
                print(f"   Resposta: {login_response.text}")
        
        # 4. Testar endpoint de conexão da API
        print("\n🔌 TESTANDO ENDPOINT DE CONEXÃO DA API:")
        print("-" * 40)
        
        # Verificar se existe endpoint para testar conexão
        try:
            test_connection_response = session.post(f"{base_url}/api/test-bitget-connection")
            print(f"Status do teste de conexão: {test_connection_response.status_code}")
            
            if test_connection_response.status_code == 200:
                connection_data = test_connection_response.json()
                print(f"✅ Teste de conexão: {connection_data}")
            else:
                print(f"❌ Erro no teste de conexão: {test_connection_response.text}")
        except Exception as e:
            print(f"⚠️  Endpoint de teste de conexão não disponível: {e}")
        
        # 5. Verificar logs do servidor
        print("\n📋 VERIFICANDO POSSÍVEIS PROBLEMAS:")
        print("-" * 40)
        
        common_issues = [
            "🔐 Criptografia das credenciais falhando",
            "🌐 Validação da API Bitget falhando",
            "💾 Salvamento no banco de dados falhando",
            "🔄 Sessão não persistindo as mudanças",
            "🔑 Chave de criptografia incorreta",
            "📡 Problemas de conectividade com Bitget"
        ]
        
        print("Possíveis causas do problema:")
        for issue in common_issues:
            print(f"   {issue}")
        
        print(f"\n🎯 RECOMENDAÇÕES:")
        print("-" * 40)
        print("1. Verificar logs do servidor durante a configuração")
        print("2. Testar credenciais da API Bitget manualmente")
        print("3. Verificar se a chave de criptografia está correta")
        print("4. Confirmar se o banco de dados está sendo atualizado")
        print("5. Verificar se há problemas de sessão/autenticação")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 DIAGNÓSTICO DE PROBLEMAS NA CONFIGURAÇÃO DA API")
    print("Problema: Credenciais aparecem como salvas mas não funcionam")
    print()
    
    success = diagnose_api_configuration()
    
    if success:
        print(f"\n{'='*60}")
        print("✅ Diagnóstico concluído!")
        print("📋 Verifique as recomendações acima para resolver o problema")
    else:
        print(f"\n{'='*60}")
        print("❌ Problemas encontrados no diagnóstico!")
    
    print(f"\n🏁 DIAGNÓSTICO FINALIZADO")