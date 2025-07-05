#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de API Segura para Gerenciamento de Credenciais
Fornece endpoints seguros para salvar, validar e restaurar credenciais da API
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, session
from functools import wraps

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db
from models.user import User
from services.credential_monitor import credential_monitor
from utils.api_persistence import APIPersistence
from utils.security import decrypt_api_key, encrypt_api_key
from dotenv import load_dotenv

class SecureAPIService:
    """Serviço de API segura para credenciais"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.api_persistence = APIPersistence()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializa o serviço com a aplicação Flask"""
        self.app = app
        
        # Registrar blueprints/rotas
        self.register_routes()
    
    def require_login(self, f):
        """Decorator para exigir login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({
                    'success': False,
                    'error': 'Login necessário',
                    'code': 'UNAUTHORIZED'
                }), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def validate_api_credentials(self, api_key: str, api_secret: str, passphrase: str) -> Dict[str, any]:
        """Valida formato das credenciais da API"""
        errors = []
        
        if not api_key or len(api_key.strip()) < 10:
            errors.append('API Key deve ter pelo menos 10 caracteres')
        
        if not api_secret or len(api_secret.strip()) < 10:
            errors.append('API Secret deve ter pelo menos 10 caracteres')
        
        if not passphrase or len(passphrase.strip()) < 3:
            errors.append('Passphrase deve ter pelo menos 3 caracteres')
        
        # Verificar caracteres especiais perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        for field_name, field_value in [('API Key', api_key), ('API Secret', api_secret), ('Passphrase', passphrase)]:
            if any(char in field_value for char in dangerous_chars):
                errors.append(f'{field_name} contém caracteres não permitidos')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def register_routes(self):
        """Registra as rotas da API"""
        
        @self.app.route('/api/credentials/save', methods=['POST'])
        @self.require_login
        def save_credentials():
            """Salva credenciais da API de forma segura"""
            try:
                user_id = session['user_id']
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        'success': False,
                        'error': 'Dados não fornecidos',
                        'code': 'INVALID_DATA'
                    }), 400
                
                api_key = data.get('api_key', '').strip()
                api_secret = data.get('api_secret', '').strip()
                passphrase = data.get('passphrase', '').strip()
                
                # Validar credenciais
                validation = self.validate_api_credentials(api_key, api_secret, passphrase)
                if not validation['valid']:
                    return jsonify({
                        'success': False,
                        'error': 'Credenciais inválidas',
                        'details': validation['errors'],
                        'code': 'VALIDATION_ERROR'
                    }), 400
                
                # Salvar com segurança
                success = credential_monitor.secure_save_credentials(
                    user_id, api_key, api_secret, passphrase
                )
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Credenciais salvas com sucesso',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Falha ao salvar credenciais',
                        'code': 'SAVE_ERROR'
                    }), 500
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro interno: {str(e)}',
                    'code': 'INTERNAL_ERROR'
                }), 500
        
        @self.app.route('/api/credentials/validate', methods=['GET'])
        @self.require_login
        def validate_credentials():
            """Valida as credenciais atuais do usuário"""
            try:
                user_id = session['user_id']
                
                # Verificar credenciais
                result = credential_monitor.check_user_credentials(
                    User.query.get(user_id)
                )
                
                return jsonify({
                    'success': True,
                    'valid': result.get('valid', False),
                    'error': result.get('error'),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro ao validar credenciais: {str(e)}',
                    'code': 'VALIDATION_ERROR'
                }), 500
        
        @self.app.route('/api/credentials/status', methods=['GET'])
        @self.require_login
        def get_credentials_status():
            """Retorna o status das credenciais do usuário"""
            try:
                user_id = session['user_id']
                user = User.query.get(user_id)
                
                if not user:
                    return jsonify({
                        'success': False,
                        'error': 'Usuário não encontrado',
                        'code': 'USER_NOT_FOUND'
                    }), 404
                
                # Verificar se tem credenciais
                has_credentials = bool(
                    user.bitget_api_key_encrypted and 
                    user.bitget_api_secret_encrypted and 
                    user.bitget_passphrase_encrypted
                )
                
                status = {
                    'has_credentials': has_credentials,
                    'user_email': user.email,
                    'timestamp': datetime.now().isoformat()
                }
                
                if has_credentials:
                    # Verificar integridade
                    validation = credential_monitor.check_user_credentials(user)
                    status.update({
                        'valid': validation.get('valid', False),
                        'error': validation.get('error'),
                        'can_decrypt': validation.get('can_decrypt', False)
                    })
                
                return jsonify({
                    'success': True,
                    'status': status
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro ao obter status: {str(e)}',
                    'code': 'STATUS_ERROR'
                }), 500

secure_api_service = SecureAPIService()