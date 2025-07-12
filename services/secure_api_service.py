#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de API Segura para Gerenciamento de Credenciais - VERSÃO CORRIGIDA
Usa apenas SQLAlchemy, sem dependências do APIPersistence
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
from utils.security import decrypt_api_key, encrypt_api_key
from api.bitget_client import BitgetAPI
from dotenv import load_dotenv

class SecureAPIService:
    """Serviço de API segura para credenciais - VERSÃO CORRIGIDA"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        
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
    
    def secure_save_credentials(self, user_id: int, api_key: str, api_secret: str, passphrase: str) -> bool:
        """Salva credenciais de forma segura usando apenas SQLAlchemy"""
        try:
            # Criptografar novas credenciais
            encrypted_key = encrypt_api_key(api_key)
            encrypted_secret = encrypt_api_key(api_secret)
            encrypted_passphrase = encrypt_api_key(passphrase)
            
            if not all([encrypted_key, encrypted_secret, encrypted_passphrase]):
                print(f"❌ Falha na criptografia das credenciais do usuário {user_id}")
                return False
            
            # Atualizar no banco de dados usando SQLAlchemy
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Usuário {user_id} não encontrado")
                return False
            
            user.bitget_api_key_encrypted = encrypted_key
            user.bitget_api_secret_encrypted = encrypted_secret
            user.bitget_passphrase_encrypted = encrypted_passphrase
            
            db.session.commit()
            
            print(f"✅ Credenciais salvas com segurança para usuário {user.email}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar credenciais do usuário {user_id}: {e}")
            db.session.rollback()
            return False
    
    def validate_user_credentials(self, user_id: int) -> Dict[str, any]:
        """Valida credenciais do usuário usando apenas SQLAlchemy"""
        try:
            # Buscar usuário usando SQLAlchemy
            user = User.query.get(user_id)
            
            if not user:
                return {
                    'valid': False,
                    'error': 'Usuário não encontrado',
                    'has_credentials': False
                }
            
            # Verificar se todas as credenciais existem
            api_key_enc = user.bitget_api_key_encrypted
            secret_enc = user.bitget_api_secret_encrypted
            passphrase_enc = user.bitget_passphrase_encrypted
            
            has_all_credentials = all([api_key_enc, secret_enc, passphrase_enc])
            
            if not has_all_credentials:
                return {
                    'valid': False,
                    'error': 'Credenciais incompletas',
                    'has_credentials': False,
                    'missing': {
                        'api_key': not bool(api_key_enc),
                        'secret': not bool(secret_enc),
                        'passphrase': not bool(passphrase_enc)
                    }
                }
            
            # Tentar descriptografar
            try:
                api_key = decrypt_api_key(api_key_enc)
                secret = decrypt_api_key(secret_enc)
                passphrase = decrypt_api_key(passphrase_enc)
                
                decryption_success = all([api_key, secret, passphrase])
                
                return {
                    'valid': decryption_success,
                    'has_credentials': True,
                    'can_decrypt': decryption_success,
                    'error': None if decryption_success else 'Falha na descriptografia'
                }
                
            except Exception as e:
                return {
                    'valid': False,
                    'has_credentials': True,
                    'can_decrypt': False,
                    'error': f'Erro na descriptografia: {str(e)}'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'Erro na validação: {str(e)}',
                'has_credentials': False
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
                success = self.secure_save_credentials(user_id, api_key, api_secret, passphrase)
                
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
                result = self.validate_user_credentials(user_id)
                
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
                
                # Verificar credenciais usando a nova validação
                validation = self.validate_user_credentials(user_id)
                
                user = User.query.get(user_id)
                if not user:
                    return jsonify({
                        'success': False,
                        'error': 'Usuário não encontrado',
                        'code': 'USER_NOT_FOUND'
                    }), 404
                
                status = {
                    'has_credentials': validation.get('has_credentials', False),
                    'valid': validation.get('valid', False),
                    'can_decrypt': validation.get('can_decrypt', False),
                    'error': validation.get('error'),
                    'user_email': user.email,
                    'timestamp': datetime.now().isoformat()
                }
                
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
        
        @self.app.route('/api/credentials/test-connection', methods=['POST'])
        @self.require_login
        def test_api_connection():
            """Testa a conexão com a API Bitget"""
            try:
                user_id = session['user_id']
                
                # Obter credenciais do usuário
                user = User.query.get(user_id)
                if not user:
                    return jsonify({
                        'success': False,
                        'error': 'Usuário não encontrado',
                        'code': 'USER_NOT_FOUND'
                    }), 404
                
                # Verificar se tem credenciais
                if not all([user.bitget_api_key_encrypted, user.bitget_api_secret_encrypted, user.bitget_passphrase_encrypted]):
                    return jsonify({
                        'success': False,
                        'error': 'Credenciais não configuradas',
                        'code': 'NO_CREDENTIALS'
                    }), 400
                
                # Descriptografar credenciais
                try:
                    api_key = decrypt_api_key(user.bitget_api_key_encrypted)
                    api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
                    passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Erro na descriptografia: {str(e)}',
                        'code': 'DECRYPTION_ERROR'
                    }), 500
                
                # Testar conexão com a API
                try:
                    bitget_client = BitgetAPI(api_key, api_secret, passphrase)
                    
                    # Testar uma chamada simples
                    account_info = bitget_client.get_account_info()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Conexão com a API Bitget estabelecida com sucesso',
                        'account_info': account_info,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Erro ao conectar com a API Bitget: {str(e)}',
                        'code': 'API_CONNECTION_ERROR'
                    }), 500
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro interno: {str(e)}',
                    'code': 'INTERNAL_ERROR'
                }), 500
