#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask Simples - Sistema BigWhale
Versão para desenvolvimento local
"""

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

# Carregar variáveis de ambiente
load_dotenv()

# Variável global para armazenar credenciais (em produção, usar banco de dados)
user_credentials = {
    "bitget_api_key": "",
    "bitget_api_secret": "",
    "bitget_passphrase": "",
    "api_configured": False
}

# Criar aplicação Flask
app = Flask(__name__)

# Configuração básica
app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração CORS correta para desenvolvimento
CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Origens específicas
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Garantir que o diretório instance existe
os.makedirs('instance', exist_ok=True)

# Rota de teste
@app.route('/api/test')
def test():
    return jsonify({"message": "Backend funcionando!", "status": "ok"})

# Rota de health check
@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Sistema BigWhale funcionando",
        "environment": "development",
        "timestamp": "2025-07-18T17:00:00"
    })

# Rota de login simples para teste
@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Responder ao preflight request
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Credenciais de teste
        valid_credentials = [
            {'email': 'admin@bigwhale.com', 'password': 'Raikamaster1@', 'name': 'Admin BigWhale', 'is_admin': True, 'id': 1},
            {'email': 'willian@lexxusadm.com.br', 'password': 'Bigwhale202021@', 'name': 'Willian Admin', 'is_admin': True, 'id': 2},
            {'email': 'financeiro@lexxusadm.com.br', 'password': 'FinanceiroDemo2025@', 'name': 'Conta Demo Financeiro', 'is_admin': False, 'id': 3}
        ]
        
        user_found = None
        for cred in valid_credentials:
            if email == cred['email'] and password == cred['password']:
                user_found = cred
                break
        
        if user_found:
            return jsonify({
                "success": True,
                "message": "Login realizado com sucesso",
                "user": {
                    "id": user_found['id'],
                    "email": email,
                    "full_name": user_found['name'],
                    "is_admin": user_found['is_admin']
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "Credenciais inválidas"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro no login: {str(e)}"
        }), 500

# Rota para verificar sessão
@app.route('/api/auth/session')
def session():
    return jsonify({
        "authenticated": False,
        "message": "Sessão não autenticada"
    })

# Rota para atualizar perfil
@app.route('/api/auth/profile', methods=['GET', 'PUT', 'OPTIONS'])
def profile():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        return response
    
    if request.method == 'GET':
        return jsonify({
            "success": True,
            "user": {
                "id": 1,
                "email": "admin@bigwhale.com",
                "full_name": "Admin BigWhale",
                "is_admin": True,
                "bitget_api_key": "***hidden***" if user_credentials["bitget_api_key"] else "",
                "bitget_api_secret": "***hidden***" if user_credentials["bitget_api_secret"] else "",
                "bitget_passphrase": "***hidden***" if user_credentials["bitget_passphrase"] else "",
                "api_configured": user_credentials["api_configured"]
            }
        })
    
    if request.method == 'PUT':
        data = request.get_json()
        print(f"🔧 Dados recebidos no PUT /api/auth/profile: {data}")
        
        # Atualizar credenciais globais
        if 'bitget_api_key' in data:
            user_credentials["bitget_api_key"] = data.get('bitget_api_key', '')
            print(f"🔑 API Key salva: {user_credentials['bitget_api_key'][:10]}..." if user_credentials["bitget_api_key"] else "🔑 API Key vazia")
        
        if 'bitget_api_secret' in data:
            user_credentials["bitget_api_secret"] = data.get('bitget_api_secret', '')
            print(f"🔐 API Secret salva: {user_credentials['bitget_api_secret'][:10]}..." if user_credentials["bitget_api_secret"] else "🔐 API Secret vazio")
        
        if 'bitget_passphrase' in data:
            user_credentials["bitget_passphrase"] = data.get('bitget_passphrase', '')
            print(f"🔒 Passphrase salva: {user_credentials['bitget_passphrase'][:10]}..." if user_credentials["bitget_passphrase"] else "🔒 Passphrase vazio")
        
        # Verificar se todas as credenciais estão configuradas
        user_credentials["api_configured"] = bool(
            user_credentials["bitget_api_key"] and 
            user_credentials["bitget_api_secret"] and 
            user_credentials["bitget_passphrase"]
        )
        
        print(f"✅ API Configurada: {user_credentials['api_configured']}")
        print(f"📊 Estado atual das credenciais: {user_credentials}")
        
        # Simular atualização do perfil
        updated_user = {
            "id": 1,
            "email": "admin@bigwhale.com",
            "full_name": data.get('full_name', 'Admin BigWhale'),
            "is_admin": True,
            "bitget_api_key": "***hidden***" if user_credentials["bitget_api_key"] else "",
            "bitget_api_secret": "***hidden***" if user_credentials["bitget_api_secret"] else "",
            "bitget_passphrase": "***hidden***" if user_credentials["bitget_passphrase"] else "",
            "api_configured": user_credentials["api_configured"]
        }
        
        return jsonify({
            "success": True,
            "message": "Perfil atualizado com sucesso",
            "user": updated_user
        })

# Rotas do Dashboard
@app.route('/api/dashboard/stats', methods=['GET', 'OPTIONS'])
def dashboard_stats():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "success": True,
        "stats": {
            "total_trades": 150,
            "winning_trades": 95,
            "losing_trades": 55,
            "win_rate": 63.33,
            "total_profit": 1250.50,
            "total_loss": -450.25,
            "net_profit": 800.25,
            "average_profit": 13.16,
            "average_loss": -8.18,
            "profit_factor": 2.78
        }
    })

@app.route('/api/dashboard/account-balance', methods=['GET', 'OPTIONS'])
def account_balance():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "success": True,
        "balance": {
            "total_balance": 5000.00,
            "available_balance": 3500.00,
            "margin_balance": 1500.00,
            "unrealized_pnl": 125.50,
            "realized_pnl": 800.25,
            "currency": "USDT"
        }
    })

@app.route('/api/dashboard/open-positions', methods=['GET', 'OPTIONS'])
def open_positions():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "success": True,
        "positions": [
            {
                "symbol": "BTCUSDT",
                "side": "LONG",
                "size": 0.1,
                "entry_price": 45000.00,
                "current_price": 45250.00,
                "unrealized_pnl": 25.00,
                "pnl_percentage": 0.56,
                "leverage": 10,
                "margin": 450.00
            },
            {
                "symbol": "ETHUSDT",
                "side": "SHORT",
                "size": 1.0,
                "entry_price": 3200.00,
                "current_price": 3180.00,
                "unrealized_pnl": 20.00,
                "pnl_percentage": 0.63,
                "leverage": 5,
                "margin": 640.00
            }
        ]
    })

@app.route('/api/dashboard/nautilus-operacional/active-operations', methods=['GET', 'OPTIONS'])
def nautilus_operations():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "success": True,
        "operations": [
            {
                "id": 1,
                "symbol": "BTCUSDT",
                "strategy": "Scalping",
                "status": "ACTIVE",
                "entry_time": "2025-07-18T15:30:00Z",
                "current_pnl": 15.50,
                "target_profit": 50.00,
                "stop_loss": -25.00
            }
        ]
    })

@app.route('/api/dashboard/credentials/status', methods=['GET', 'OPTIONS'])
def credentials_status():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "success": True,
        "credentials": {
            "api_key_configured": user_credentials["api_configured"],
            "api_key_valid": user_credentials["api_configured"],
            "permissions": ["READ", "TRADE"] if user_credentials["api_configured"] else [],
            "last_validation": "2025-07-18T17:00:00Z" if user_credentials["api_configured"] else None
        }
    })

@app.route('/api/credentials', methods=['GET', 'OPTIONS'])
def credentials():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "success": True,
        "credentials": {
            "api_key": user_credentials["bitget_api_key"] or "***hidden***",
            "secret_key": user_credentials["bitget_api_secret"] or "***hidden***",
            "passphrase": user_credentials["bitget_passphrase"] or "***hidden***",
            "exchange": "bitget",
            "testnet": False,
            "configured": user_credentials["api_configured"]
        }
    })

@app.route('/api/dashboard/sync-trades', methods=['POST', 'OPTIONS'])
def sync_trades():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Simular sincronização de trades
        return jsonify({
            "success": True,
            "message": "Trades sincronizados com sucesso",
            "trades_synced": 25,
            "last_sync": "2025-07-18T18:30:00Z"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao sincronizar trades: {str(e)}"
        }), 500

@app.route('/api/dashboard/nautilus-operacional/monitor-targets', methods=['GET', 'OPTIONS'])
def monitor_targets():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "success": True,
        "targets": [
            {
                "id": 1,
                "symbol": "BTCUSDT",
                "target_price": 46000.00,
                "current_price": 45250.00,
                "status": "MONITORING",
                "created_at": "2025-07-18T15:00:00Z",
                "strategy": "Breakout"
            },
            {
                "id": 2,
                "symbol": "ETHUSDT",
                "target_price": 3300.00,
                "current_price": 3180.00,
                "status": "MONITORING",
                "created_at": "2025-07-18T16:00:00Z",
                "strategy": "Support"
            }
        ]
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor BigWhale...")
    print("🌐 URL: http://localhost:5000")
    print("📊 Health: http://localhost:5000/api/health")
    print("🔑 Login: http://localhost:5000/api/auth/login")
    print("⚠️  Para parar: Ctrl+C")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    ) 