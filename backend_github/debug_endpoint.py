#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoint de debug simplificado para testar o login sem dependências complexas
"""

from flask import Flask, request, jsonify
import os
import traceback
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'debug-key'

# Simular dados de usuário admin
ADMIN_USER = {
    'id': 1,
    'email': 'admin@bigwhale.com',
    'password_hash': generate_password_hash('Raikamaster1@'),
    'full_name': 'Admin BigWhale',
    'is_admin': True,
    'is_active': True
}

@app.route('/api/health')
def health_check():
    """Health check simplificado"""
    return jsonify({
        'status': 'healthy',
        'message': 'Debug endpoint funcionando',
        'environment': 'debug'
    }), 200

@app.route('/api/auth/login', methods=['POST'])
def debug_login():
    """Login simplificado para debug"""
    try:
        print("=== DEBUG LOGIN INICIADO ===")
        
        # 1. Verificar se recebeu dados JSON
        if not request.is_json:
            print("❌ Request não é JSON")
            return jsonify({'message': 'Content-Type deve ser application/json'}), 400
            
        data = request.get_json()
        print(f"✅ Dados recebidos: {data}")
        
        # 2. Validar campos obrigatórios
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            print("❌ Email ou senha não fornecidos")
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400
            
        print(f"✅ Email: {email}")
        print(f"✅ Password fornecida: {'Sim' if password else 'Não'}")
        
        # 3. Verificar credenciais
        if email != ADMIN_USER['email']:
            print(f"❌ Email não encontrado: {email}")
            return jsonify({'message': 'Email ou senha inválidos'}), 401
            
        if not check_password_hash(ADMIN_USER['password_hash'], password):
            print("❌ Senha incorreta")
            return jsonify({'message': 'Email ou senha inválidos'}), 401
            
        print("✅ Credenciais válidas")
        
        # 4. Simular resposta de sucesso
        response_data = {
            'message': 'Login realizado com sucesso (DEBUG)',
            'user': {
                'id': ADMIN_USER['id'],
                'email': ADMIN_USER['email'],
                'full_name': ADMIN_USER['full_name'],
                'is_admin': ADMIN_USER['is_admin'],
                'is_active': ADMIN_USER['is_active'],
                'api_configured': False,
                'session_token': 'debug-session-token-12345'
            }
        }
        
        print(f"✅ Resposta preparada: {response_data}")
        print("=== DEBUG LOGIN CONCLUÍDO COM SUCESSO ===")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print("=== ERRO NO DEBUG LOGIN ===")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        print("=== FIM DO ERRO ===")
        
        return jsonify({
            'message': 'Erro interno no servidor (DEBUG)',
            'error_type': type(e).__name__,
            'error_message': str(e)
        }), 500

@app.route('/api/auth/session', methods=['GET'])
def debug_session():
    """Verificação de sessão simplificada"""
    return jsonify({
        'authenticated': False,
        'message': 'Debug session endpoint'
    }), 200

@app.route('/api/test')
def test_route():
    """Rota de teste"""
    return jsonify({
        'message': 'Debug backend funcionando!',
        'environment': 'debug'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando servidor debug na porta {port}")
    print("📧 Credenciais de teste:")
    print("   Email: admin@bigwhale.com")
    print("   Senha: Raikamaster1@")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )