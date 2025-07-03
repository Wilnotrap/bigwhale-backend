#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from flask import Flask
    from database import db
    from models.user import User
    from models.session import UserSession
    from utils.security import decrypt_api_key
    from dotenv import load_dotenv
    
    print("✅ Todas as importações foram bem-sucedidas")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurar Flask app básico
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key')
    app.config['AES_ENCRYPTION_KEY'] = os.getenv('AES_ENCRYPTION_KEY', '12345678901234567890123456789012')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:\\Nautilus Aut\\back\\backend\\instance\\site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar banco
    db.init_app(app)
    
    with app.app_context():
        print("✅ Contexto do Flask criado com sucesso")
        
        # Testar conexão com banco
        try:
            users = User.query.all()
            print(f"✅ Conexão com banco OK - {len(users)} usuários encontrados")
        except Exception as e:
            print(f"❌ Erro na conexão com banco: {e}")
            
        # Testar sessões
        try:
            sessions = UserSession.query.all()
            print(f"✅ Tabela de sessões OK - {len(sessions)} sessões encontradas")
        except Exception as e:
            print(f"❌ Erro na tabela de sessões: {e}")
            
        # Testar criptografia
        try:
            test_result = decrypt_api_key(None)
            print(f"✅ Função de descriptografia OK - resultado para None: {test_result}")
        except Exception as e:
            print(f"❌ Erro na função de descriptografia: {e}")
            
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()