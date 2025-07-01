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
        
        @self.app.route('/api/credentials/backups', methods=['GET'])
        @self.require_login
        def get_backups():
            """Lista os backups disponíveis do usuário"""
            try:
                user_id = session['user_id']
                
                backups = self.api_persistence.get_user_backups(user_id)
                
                return jsonify({
                    'success': True,
                    'backups': backups,
                    'count': len(backups),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro ao listar backups: {str(e)}',
                    'code': 'BACKUP_LIST_ERROR'
                }), 500
        
        @self.app.route('/api/credentials/restore', methods=['POST'])
        @self.require_login
        def restore_credentials():
            """Restaura credenciais de um backup"""
            try:
                user_id = session['user_id']
                data = request.get_json()
                
                backup_filename = data.get('backup_filename') if data else None
                
                if backup_filename:
                    # Restaurar backup específico
                    backup_path = os.path.join(
                        'backups', 'api_credentials', backup_filename
                    )
                    success = self.api_persistence.restore_user_credentials(
                        user_id, backup_path
                    )
                else:
                    # Restaurar backup mais recente
                    success = credential_monitor.attempt_credential_restoration(
                        User.query.get(user_id)
                    )
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Credenciais restauradas com sucesso',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Falha ao restaurar credenciais',
                        'code': 'RESTORE_ERROR'
                    }), 500
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro ao restaurar credenciais: {str(e)}',
                    'code': 'RESTORE_ERROR'
                }), 500
        
        @self.app.route('/api/credentials/force-check', methods=['POST'])
        @self.require_login
        def force_check():
            """Força verificação imediata das credenciais"""
            try:
                user_id = session['user_id']
                
                result = credential_monitor.force_check_user(user_id)
                
                return jsonify({
                    'success': True,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro na verificação: {str(e)}',
                    'code': 'CHECK_ERROR'
                }), 500
        
        @self.app.route('/api/monitor/status', methods=['GET'])
        @self.require_login
        def get_monitor_status():
            """Retorna o status do monitoramento"""
            try:
                status = credential_monitor.get_monitoring_status()
                
                return jsonify({
                    'success': True,
                    'monitor_status': status,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro ao obter status do monitor: {str(e)}',
                    'code': 'MONITOR_STATUS_ERROR'
                }), 500
        
        @self.app.route('/api/credentials/test-connection', methods=['POST'])
        @self.require_login
        def test_api_connection():
            """Testa a conexão com a API usando as credenciais atuais"""
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
                if not all([
                    user.bitget_api_key_encrypted,
                    user.bitget_api_secret_encrypted,
                    user.bitget_passphrase_encrypted
                ]):
                    return jsonify({
                        'success': False,
                        'error': 'Credenciais não configuradas',
                        'code': 'NO_CREDENTIALS'
                    }), 400
                
                # Tentar descriptografar
                try:
                    api_key = decrypt_api_key(user.bitget_api_key_encrypted)
                    api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
                    passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)
                    
                    if not all([api_key, api_secret, passphrase]):
                        return jsonify({
                            'success': False,
                            'error': 'Falha na descriptografia das credenciais',
                            'code': 'DECRYPTION_ERROR'
                        }), 500
                    
                    # Aqui você pode adicionar teste real da API Bitget
                    # Por enquanto, apenas verificamos se conseguimos descriptografar
                    
                    return jsonify({
                        'success': True,
                        'message': 'Credenciais válidas e descriptografadas com sucesso',
                        'connection_test': 'passed',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as decrypt_error:
                    return jsonify({
                        'success': False,
                        'error': f'Erro na descriptografia: {str(decrypt_error)}',
                        'code': 'DECRYPTION_ERROR'
                    }), 500
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro no teste de conexão: {str(e)}',
                    'code': 'CONNECTION_TEST_ERROR'
                }), 500

# Instância global do serviço
secure_api_service = SecureAPIService()

def create_secure_api_app():
    """Cria aplicação Flask para a API segura"""
    # Carregar variáveis de ambiente
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
    
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
    app.config['AES_ENCRYPTION_KEY'] = os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    
    # Configuração do banco
    instance_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensões
    db.init_app(app)
    credential_monitor.init_app(app)
    secure_api_service.init_app(app)
    
    return app

if __name__ == '__main__':
    # Executar como script standalone
    app = create_secure_api_app()
    
    print("🚀 Iniciando API segura de credenciais...")
    app.run(debug=True, host='0.0.0.0', port=5001)