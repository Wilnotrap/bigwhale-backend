"""
Serviço para gerenciar credenciais da API Bitget de forma centralizada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from utils.security import decrypt_api_key, encrypt_api_key
from api.bitget_client import BitgetAPI
from database import db
from flask import current_app
import logging

class APICredentialsService:
    """Serviço para gerenciar credenciais da API Bitget"""
    
    def __init__(self):
        self.logger = current_app.logger if current_app else logging.getLogger(__name__)
    
    def load_user_credentials(self, user_id=None, email=None):
        """
        Carrega e descriptografa as credenciais da API de um usuário
        
        Args:
            user_id: ID do usuário (opcional)
            email: Email do usuário (opcional)
            
        Returns:
            dict: Dicionário com as credenciais ou None se não encontradas
        """
        try:
            # Buscar usuário por ID ou email
            if user_id:
                user = User.query.get(user_id)
            elif email:
                user = User.query.filter_by(email=email).first()
            else:
                self.logger.error("É necessário fornecer user_id ou email")
                return None
                
            if not user:
                self.logger.warning(f"Usuário não encontrado - ID: {user_id}, Email: {email}")
                return None
            
            # Verificar se o usuário tem credenciais salvas
            if not (user.bitget_api_key_encrypted and 
                   user.bitget_api_secret_encrypted and 
                   user.bitget_passphrase_encrypted):
                self.logger.info(f"Usuário {user.id} não possui credenciais da API configuradas")
                return {
                    'user_id': user.id,
                    'email': user.email,
                    'has_credentials': False,
                    'api_key': None,
                    'api_secret': None,
                    'passphrase': None,
                    'is_valid': False
                }
            
            # Descriptografar credenciais
            api_key = decrypt_api_key(user.bitget_api_key_encrypted)
            api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
            passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)
            
            # Verificar se a descriptografia foi bem-sucedida
            if not (api_key and api_secret and passphrase):
                self.logger.error(f"Falha na descriptografia das credenciais do usuário {user.id}")
                return {
                    'user_id': user.id,
                    'email': user.email,
                    'has_credentials': True,
                    'api_key': None,
                    'api_secret': None,
                    'passphrase': None,
                    'is_valid': False,
                    'error': 'Falha na descriptografia'
                }
            
            self.logger.info(f"Credenciais carregadas com sucesso para usuário {user.id}")
            
            return {
                'user_id': user.id,
                'email': user.email,
                'has_credentials': True,
                'api_key': api_key,
                'api_secret': api_secret,
                'passphrase': passphrase,
                'is_valid': True
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar credenciais: {str(e)}")
            return None
    
    def validate_credentials(self, credentials):
        """
        Valida credenciais da API usando o cliente Bitget
        
        Args:
            credentials: Dicionário com as credenciais
            
        Returns:
            bool: True se válidas, False caso contrário
        """
        try:
            if not credentials or not credentials.get('is_valid'):
                return False
                
            api_key = credentials.get('api_key')
            api_secret = credentials.get('api_secret')
            passphrase = credentials.get('passphrase')
            
            if not (api_key and api_secret and passphrase):
                return False
            
            # Testar credenciais com cliente Bitget
            bitget_client = BitgetAPI(
                api_key=api_key,
                secret_key=api_secret,
                passphrase=passphrase
            )
            
            is_valid = bitget_client.validate_credentials()
            self.logger.info(f"Validação de credenciais: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Erro ao validar credenciais: {str(e)}")
            return False
    
    def save_credentials(self, user_id, api_key, api_secret, passphrase, validate=True):
        """
        Salva credenciais da API para um usuário
        
        Args:
            user_id: ID do usuário
            api_key: Chave da API
            api_secret: Segredo da API
            passphrase: Passphrase da API
            validate: Se deve validar as credenciais antes de salvar
            
        Returns:
            dict: Resultado da operação
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado'
                }
            
            # Validar credenciais se solicitado
            if validate:
                test_credentials = {
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'passphrase': passphrase,
                    'is_valid': True
                }
                
                if not self.validate_credentials(test_credentials):
                    return {
                        'success': False,
                        'error': 'Credenciais da API inválidas'
                    }
            
            # Criptografar e salvar
            encrypted_key = encrypt_api_key(api_key.strip())
            encrypted_secret = encrypt_api_key(api_secret.strip())
            encrypted_passphrase = encrypt_api_key(passphrase.strip())
            
            if not (encrypted_key and encrypted_secret and encrypted_passphrase):
                return {
                    'success': False,
                    'error': 'Falha na criptografia das credenciais'
                }
            
            user.bitget_api_key_encrypted = encrypted_key
            user.bitget_api_secret_encrypted = encrypted_secret
            user.bitget_passphrase_encrypted = encrypted_passphrase
            
            db.session.commit()
            
            # Verificar se foram salvas corretamente
            saved_credentials = self.load_user_credentials(user_id=user_id)
            if saved_credentials and saved_credentials.get('is_valid'):
                self.logger.info(f"Credenciais salvas com sucesso para usuário {user_id}")
                return {
                    'success': True,
                    'message': 'Credenciais salvas com sucesso',
                    'credentials': saved_credentials
                }
            else:
                return {
                    'success': False,
                    'error': 'Falha na verificação das credenciais salvas'
                }
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erro ao salvar credenciais: {str(e)}")
            return {
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }
    
    def sync_credentials_by_email(self, email):
        """
        Sincroniza credenciais de um usuário baseado no email
        Útil para garantir que após login as credenciais estejam disponíveis
        
        Args:
            email: Email do usuário
            
        Returns:
            dict: Resultado da sincronização
        """
        try:
            credentials = self.load_user_credentials(email=email)
            
            if not credentials:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado'
                }
            
            if not credentials.get('has_credentials'):
                return {
                    'success': True,
                    'message': 'Usuário não possui credenciais configuradas',
                    'credentials': credentials
                }
            
            if not credentials.get('is_valid'):
                return {
                    'success': False,
                    'error': 'Credenciais não puderam ser carregadas corretamente',
                    'credentials': credentials
                }
            
            # Validar credenciais
            is_valid = self.validate_credentials(credentials)
            credentials['api_validated'] = is_valid
            
            self.logger.info(f"Sincronização de credenciais para {email}: sucesso")
            
            return {
                'success': True,
                'message': 'Credenciais sincronizadas com sucesso',
                'credentials': credentials
            }
            
        except Exception as e:
            self.logger.error(f"Erro na sincronização de credenciais para {email}: {str(e)}")
            return {
                'success': False,
                'error': f'Erro na sincronização: {str(e)}'
            }
    
    def get_user_api_status(self, user_id):
        """
        Retorna o status das credenciais da API de um usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            dict: Status das credenciais
        """
        try:
            credentials = self.load_user_credentials(user_id=user_id)
            
            if not credentials:
                return {
                    'configured': False,
                    'valid': False,
                    'status': 'not_found'
                }
            
            if not credentials.get('has_credentials'):
                return {
                    'configured': False,
                    'valid': False,
                    'status': 'not_configured'
                }
            
            if not credentials.get('is_valid'):
                return {
                    'configured': True,
                    'valid': False,
                    'status': 'invalid'
                }
            
            # Validar credenciais
            is_valid = self.validate_credentials(credentials)
            
            return {
                'configured': True,
                'valid': is_valid,
                'status': 'active' if is_valid else 'error'
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar status da API para usuário {user_id}: {str(e)}")
            return {
                'configured': False,
                'valid': False,
                'status': 'error',
                'error': str(e)
            } 