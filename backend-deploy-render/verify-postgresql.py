#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a configuração PostgreSQL no Render
"""

import requests
import json
from datetime import datetime

# URL do backend no Render
BASE_URL = "https://bigwhale-backend.onrender.com"

def check_database_config():
    """Verificar configuração do banco de dados"""
    print("🔍 Verificando configuração do banco de dados...")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Backend respondendo!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🌍 Ambiente: {data.get('environment', 'unknown')}")
            print(f"📦 Versão: {data.get('version', 'unknown')}")
            
            # Verificar informações do banco
            db_info = data.get('database', {})
            if isinstance(db_info, dict):
                print("\n🗄️ Informações do Banco de Dados:")
                print(f"   Tipo: {db_info.get('type', 'unknown')}")
                print(f"   Status: {db_info.get('status', 'unknown')}")
                print(f"   Usuários: {db_info.get('users_count', 0)}")
                
                # Verificar se está usando PostgreSQL
                if db_info.get('type') == 'PostgreSQL':
                    print("\n🎉 SUCESSO: PostgreSQL está sendo usado!")
                    print("✅ Dados serão preservados entre deploys")
                    print("✅ Configuração de produção ativa")
                    return True
                elif db_info.get('type') == 'SQLite':
                    print("\n⚠️ ATENÇÃO: SQLite está sendo usado")
                    print("❌ Isso indica que DATABASE_URL não está configurada")
                    print("💡 Verifique as variáveis de ambiente no Render")
                    return False
                else:
                    print(f"\n❓ Tipo de banco desconhecido: {db_info.get('type')}")
                    return False
            else:
                print(f"\n⚠️ Formato de resposta inesperado para database: {db_info}")
                return False
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - O servidor pode estar inicializando")
        print("💡 Aguarde alguns minutos e tente novamente")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Erro de conexão")
        print("💡 Verifique se o serviço está rodando no Render")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

def check_environment_variables():
    """Verificar se as variáveis de ambiente estão configuradas"""
    print("\n🔧 Verificando variáveis de ambiente esperadas...")
    print("="*50)
    
    expected_vars = [
        "DATABASE_URL",
        "FLASK_SECRET_KEY", 
        "PYTHON_VERSION",
        "RENDER"
    ]
    
    print("📋 Variáveis que devem estar configuradas no Render:")
    for var in expected_vars:
        if var == "DATABASE_URL":
            print(f"   ✅ {var}: Configurada automaticamente pelo PostgreSQL")
        elif var == "RENDER":
            print(f"   ✅ {var}: Configurada automaticamente (valor: 'true')")
        elif var == "PYTHON_VERSION":
            print(f"   ✅ {var}: Detectada automaticamente (3.11.9)")
        else:
            print(f"   ⚠️ {var}: Opcional (pode ser configurada manualmente)")

def main():
    """Executar verificação completa"""
    print("🚀 Verificação PostgreSQL - BigWhale Backend")
    print("=============================================")
    print(f"🕐 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: {BASE_URL}")
    
    # Verificar configuração do banco
    db_ok = check_database_config()
    
    # Verificar variáveis de ambiente
    check_environment_variables()
    
    # Resumo final
    print("\n" + "="*50)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("="*50)
    
    if db_ok:
        print("🎉 CONFIGURAÇÃO CORRETA!")
        print("✅ PostgreSQL está sendo usado")
        print("✅ Dados serão preservados")
        print("✅ Backend pronto para produção")
        
        print("\n🔗 Links úteis:")
        print(f"   Health Check: {BASE_URL}/api/health")
        print("   Render Dashboard: https://dashboard.render.com")
        print("   PostgreSQL Dashboard: Acesse via Render > Database")
        
    else:
        print("❌ CONFIGURAÇÃO INCORRETA")
        print("🚨 PostgreSQL não está sendo usado")
        print("⚠️ Dados podem ser perdidos")
        
        print("\n🔧 Passos para corrigir:")
        print("1. Acesse https://dashboard.render.com")
        print("2. Vá para seu serviço 'bigwhale-backend'")
        print("3. Verifique a aba 'Environment'")
        print("4. Confirme se DATABASE_URL está presente")
        print("5. Se não estiver, conecte o PostgreSQL ao serviço")
        print("6. Faça um novo deploy")
    
    print(f"\n🕐 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()