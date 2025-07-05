import requests
import json
from datetime import datetime, timedelta

class NautilusService:
    """
    Serviço para integração com o sistema Nautilus
    """
    
    def __init__(self):
        self.base_url = "https://bw.mdsa.com.br"
        self.admin_email = "admin@bigwhale.com"
        self.admin_password = "bigwhale"
        self.token = None
        self.user_id = None
        self.token_expires_at = None
    
    def authenticate(self):
        """Autentica com o sistema Nautilus e obtém token de acesso"""
        try:
            url = f"{self.base_url}/login"
            
            login_data = {
                "email": self.admin_email,
                "password": self.admin_password
            }
            
            response = requests.post(
                url,
                json=login_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.user_id = data.get('userId')
                
                # Assumindo que o token expira em 4 horas (padrão JWT)
                self.token_expires_at = datetime.now() + timedelta(hours=4)
                
                return {
                    'success': True,
                    'token': self.token,
                    'user_id': self.user_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Authentication failed: HTTP {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Authentication error: {str(e)}'
            }
    
    def get_nautilus_credentials(self):
        """Obtém token e user_id do sistema Nautilus para um novo usuário"""
        try:
            auth_result = self.authenticate()
            
            if auth_result['success']:
                return {
                    'success': True,
                    'token': auth_result['token'],
                    'nautilus_user_id': auth_result['user_id'],
                    'message': 'Credenciais Nautilus obtidas com sucesso'
                }
            else:
                return {
                    'success': False,
                    'error': 'Falha ao obter credenciais do Nautilus',
                    'details': auth_result.get('error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao conectar com Nautilus: {str(e)}'
            }

nautilus_service = NautilusService()