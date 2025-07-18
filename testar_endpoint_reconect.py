#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o endpoint /reconnect-api e identificar o problema
"""
import requests
import json
import sys
import sqlite3
import os
from datetime import datetime

def testar_endpoint_reconnect():
    """
    Testa o endpoint /reconnect-api para identificar o problema
    """
    print("🔍 TESTANDO ENDPOINT /reconnect-api")
    print("=" * 60)
    
    # Configurações do servidor
    base_url = "http://localhost:5000"
    
    # Primeiro, vamos verificar se há usuários com credenciais no banco
    print("\n1. VERIFICANDO USUÁRIOS COM CREDENCIAIS NO BANCO")
    print("-" * 50)
    
    # Encontrar arquivo do banco
    db_paths = [
        'backend/instance/site.db',
        'backend/instance/database.db',
        'instance/site.db',
        'instance/database.db',
        'database.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar usuários com credenciais
        cursor.execute("""
            SELECT 
                id, 
                full_name, 
                email, 
                bitget_api_key_encrypted,
                bitget_api_secret_encrypted,
                bitget_passphrase_encrypted
            FROM users
            WHERE bitget_api_key_encrypted IS NOT NULL 
            AND bitget_api_secret_encrypted IS NOT NULL 
            AND bitget_passphrase_encrypted IS NOT NULL
        """)
        
        usuarios_com_api = cursor.fetchall()
        
        if not usuarios_com_api:
            print("❌ Nenhum usuário com credenciais encontrado no banco!")
            conn.close()
            return
            
        print(f"✅ Encontrados {len(usuarios_com_api)} usuários com credenciais")
        
        # Pegar o primeiro usuário para teste
        user_id, nome, email, api_key, api_secret, passphrase = usuarios_com_api[0]
        print(f"🧪 Testando com usuário: {nome} ({email}) - ID: {user_id}")
        
        conn.close()
        
        # 2. Testar sessão mock
        print(f"\n2. TESTANDO ENDPOINT /reconnect-api")
        print("-" * 50)
        
        # Criar sessão
        session = requests.Session()
        
        # Simular login fazendo uma requisição para o endpoint de reconexão
        # Primeiro, vamos verificar se o backend está rodando
        try:
            health_check = session.get(f"{base_url}/api/dashboard/api-status", timeout=5)
            print(f"⚠️ Backend não está rodando ou não aceita requisições sem autenticação")
        except Exception as e:
            print(f"⚠️ Backend pode não estar rodando: {e}")
            print("💡 Inicie o backend primeiro: python backend/app.py")
            return
            
        # Simular autenticação criando cookie de sessão
        # Vamos tentar fazer uma requisição direta ao banco via script Python
        
        print("\n3. TESTANDO LÓGICA DE VERIFICAÇÃO DIRETAMENTE")
        print("-" * 50)
        
        # Vamos testar a lógica que o endpoint usa
        print(f"✅ Usuário tem credenciais no banco:")
        print(f"   API Key: {len(api_key)} caracteres")
        print(f"   Secret: {len(api_secret)} caracteres")
        print(f"   Passphrase: {len(passphrase)} caracteres")
        
        # Testar descriptografia
        print("\n4. TESTANDO DESCRIPTOGRAFIA")
        print("-" * 50)
        
        # Vamos tentar importar e testar a descriptografia
        try:
            # Adicionar o backend ao path
            sys.path.insert(0, os.path.abspath('backend'))
            
            from utils.security import decrypt_api_key
            
            # Testar descriptografia
            try:
                decrypted_key = decrypt_api_key(api_key)
                decrypted_secret = decrypt_api_key(api_secret)
                decrypted_passphrase = decrypt_api_key(passphrase)
                
                print(f"✅ Descriptografia bem-sucedida:")
                print(f"   API Key: {len(decrypted_key)} caracteres")
                print(f"   Secret: {len(decrypted_secret)} caracteres")
                print(f"   Passphrase: {len(decrypted_passphrase)} caracteres")
                
                # Verificar se as credenciais descriptografadas são válidas
                valid_creds = all([decrypted_key, decrypted_secret, decrypted_passphrase])
                print(f"   Credenciais válidas: {'✅' if valid_creds else '❌'}")
                
                if valid_creds:
                    print("\n5. TESTANDO CRIAÇÃO DO CLIENTE BITGET")
                    print("-" * 50)
                    
                    try:
                        from api.bitget_client import BitgetAPI
                        
                        bitget_client = BitgetAPI(
                            api_key=decrypted_key,
                            secret_key=decrypted_secret,
                            passphrase=decrypted_passphrase
                        )
                        
                        print("✅ Cliente Bitget criado com sucesso")
                        
                        # Testar validação
                        print("\n6. TESTANDO VALIDAÇÃO DAS CREDENCIAIS")
                        print("-" * 50)
                        
                        try:
                            account_info = bitget_client.get_account_info()
                            if account_info:
                                print("✅ Credenciais válidas - account_info obtido")
                                print(f"   Resposta: {json.dumps(account_info, indent=2)}")
                            else:
                                print("❌ Credenciais inválidas - account_info retornou None")
                        except Exception as e:
                            print(f"❌ Erro ao validar credenciais: {e}")
                            
                    except Exception as e:
                        print(f"❌ Erro ao criar cliente Bitget: {e}")
                        
            except Exception as e:
                print(f"❌ Erro na descriptografia: {e}")
                
        except Exception as e:
            print(f"❌ Erro ao importar módulos: {e}")
            
        print("\n" + "=" * 60)
        print("CONCLUSÃO DO TESTE")
        print("=" * 60)
        
        print("💡 Para resolver o problema:")
        print("1. Verificar se o backend está rodando")
        print("2. Verificar se a autenticação está funcionando")
        print("3. Verificar se as credenciais estão sendo descriptografadas corretamente")
        print("4. Verificar se o cliente Bitget está sendo criado corretamente")
        print("5. Verificar se há diferenças entre os endpoints")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🚀 NAUTILUS AUTOMAÇÃO - TESTE ENDPOINT RECONNECT")
    print("Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print()
    
    testar_endpoint_reconnect() 