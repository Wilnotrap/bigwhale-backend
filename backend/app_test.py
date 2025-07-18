#!/usr/bin/env python3
# app_test.py - Servidor temporário para testar endpoints Nautilus
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/dashboard/nautilus/login', methods=['POST', 'OPTIONS'])
def nautilus_login():
    """Proxy para autenticação no Nautilus"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Usar credenciais fixas do admin Nautilus
        login_data = {
            "email": "admin@bigwhale.com",
            "password": "bigwhale"
        }
        
        logger.info("Fazendo autenticação no Nautilus...")
        response = requests.post(
            "https://bw.mdsa.com.br/login",
            json=login_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        logger.info(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'token': data.get('token'),
                'userId': data.get('userId')
            })
        else:
            logger.error(f"Erro na autenticação: {response.text}")
            return jsonify({'error': 'Falha na autenticação'}), response.status_code
            
    except Exception as e:
        logger.error(f"Erro na autenticação Nautilus: {str(e)}")
        return jsonify({'error': 'Erro interno na autenticação'}), 500


@app.route('/api/dashboard/nautilus/active-operations', methods=['GET', 'OPTIONS'])
def nautilus_active_operations():
    """Proxy para operações ativas do Nautilus"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Extrair headers de autorização
        auth_token = request.headers.get('Authorization', '')
        user_id = request.headers.get('auth-userid', '')
        
        if not auth_token or not user_id:
            return jsonify({'error': 'Headers de autenticação necessários'}), 400
        
        logger.info("Buscando operações ativas do Nautilus...")
        response = requests.get(
            "https://bw.mdsa.com.br/operation/active-operations",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token,
                'auth-userid': user_id,
                'Origin': 'https://bw-admin.mdsa.com.br',
                'Referer': 'https://bw-admin.mdsa.com.br/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=30
        )
        
        logger.info(f"Status das operações: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro nas operações: {response.text}")
            return jsonify({'error': 'Erro ao buscar operações'}), response.status_code
            
    except Exception as e:
        logger.error(f"Erro nas operações ativas Nautilus: {str(e)}")
        return jsonify({'error': 'Erro interno ao buscar operações'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde"""
    return jsonify({'status': 'OK', 'message': 'Servidor Nautilus rodando'})

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste Nautilus...")
    print("📊 Endpoints disponíveis:")
    print("   - POST /api/dashboard/nautilus/login")
    print("   - GET /api/dashboard/nautilus/active-operations")
    print("   - GET /health")
    print("🔗 Rodando em: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 