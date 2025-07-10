#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("🔄 Testando inicialização do servidor...")
    
    # Importar e configurar o app
    from start_server_simple import app
    
    print("✅ App importado com sucesso")
    
    # Testar se o contexto funciona
    with app.app_context():
        print("✅ Contexto do Flask criado com sucesso")
        
        # Testar rota de saúde
        with app.test_client() as client:
            response = client.get('/health')
            print(f"✅ Rota de saúde: {response.status_code}")
            
            # Testar rota de sessão
            response = client.get('/api/auth/session')
            print(f"✅ Rota de sessão: {response.status_code} - {response.get_json()}")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()