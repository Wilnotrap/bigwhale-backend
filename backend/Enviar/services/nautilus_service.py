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
        """
        Autentica com o sistema Nautilus e obtém token de acesso
        """
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
    
    def is_token_valid(self):
        """
        Verifica se o token atual ainda é válido
        """
        if not self.token or not self.token_expires_at:
            return False
        
        # Considera válido se ainda tem pelo menos 5 minutos
        return datetime.now() < (self.token_expires_at - timedelta(minutes=5))
    
    def ensure_authenticated(self):
        """
        Garante que temos um token válido, renovando se necessário
        """
        if not self.is_token_valid():
            return self.authenticate()
        
        return {
            'success': True,
            'token': self.token,
            'user_id': self.user_id
        }
    
    def get_nautilus_credentials(self):
        """
        Obtém token e user_id do sistema Nautilus para um novo usuário
        
        Returns:
            dict: Resultado da operação com token e user_id
        """
        try:
            # Fazer autenticação para obter token e user_id
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
    
    def send_user_data_to_nautilus(self, user_data):
        """
        Envia dados do usuário para o servidor Nautilus - LÓGICA CORRIGIDA
        
        Args:
            user_data (dict): Dados do usuário contendo:
                - full_name: Nome completo
                - email: Email do usuário
                - bitget_api_key: Chave API da Bitget
                - bitget_api_secret: Secret API da Bitget
                - bitget_passphrase: Passphrase da API Bitget
        
        Returns:
            dict: Resultado do envio dos dados
        """
        try:
            print("=" * 80)
            print("🚀 NAUTILUS - INICIANDO ENVIO DE DADOS")
            print("=" * 80)
            
            # Primeiro, garantir que temos credenciais válidas
            auth_result = self.ensure_authenticated()
            if not auth_result['success']:
                print(f"❌ NAUTILUS - Falha na autenticação: {auth_result.get('error')}")
                return auth_result
            
            print(f"✅ NAUTILUS - Autenticação confirmada")
            print(f"🎫 Token: {self.token[:20] if self.token else 'N/A'}...")
            print(f"🆔 User ID: {self.user_id}")
            
            # Calcular data de expiração (30 dias após cadastro)
            expiration_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Preparar dados no formato esperado pelo servidor Nautilus
            nautilus_data = {
                "name": user_data.get('full_name'),
                "email": user_data.get('email'),
                "password": user_data.get('password', '123456'),
                "apiKey": user_data.get('bitget_api_key'),
                "apiSecret": user_data.get('bitget_api_secret'),
                "apiPass": user_data.get('bitget_passphrase'),
                "expirationDate": expiration_date,
                "defaultEntryPercentage": "5",
                "status": "active"
            }
            
            # Headers com token e ID conforme especificado
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'{self.token}',
                'auth-userid': str(self.user_id)
            }
            
            # Endpoint para envio dos dados do usuário
            url = f"{self.base_url}/user"
            
            print(f"📡 NAUTILUS - URL: {url}")
            print(f"👤 NAUTILUS - Usuário: {nautilus_data.get('name')} ({nautilus_data.get('email')})")
            print(f"🔑 NAUTILUS - API Key: {nautilus_data.get('apiKey')[:10]}..." if nautilus_data.get('apiKey') else "N/A")
            print("📤 NAUTILUS - Enviando requisição...")
            
            # Enviar dados para o Nautilus
            response = requests.post(
                url,
                data=json.dumps(nautilus_data),
                headers=headers,
                timeout=30
            )
            
            print(f"📊 NAUTILUS - Status da resposta: {response.status_code}")
            print(f"📄 NAUTILUS - Conteúdo da resposta: {response.text}")
            print(f"📋 NAUTILUS - Headers da resposta: {dict(response.headers)}")
            
            # LÓGICA CORRIGIDA - Análise rigorosa da resposta
            print("🔍 NAUTILUS - Analisando resposta...")
            
            if response.status_code in [200, 201]:
                print("🎉 NAUTILUS - SUCESSO CONFIRMADO!")
                print(f"✅ NAUTILUS - Status {response.status_code} = USUÁRIO CRIADO")
                
                # Tentar extrair dados da resposta
                nautilus_response_data = None
                try:
                    nautilus_response_data = response.json()
                    user_id_created = nautilus_response_data.get('id', 'N/A')
                    print(f"🆔 NAUTILUS - ID do usuário criado: {user_id_created}")
                except Exception as parse_error:
                    print(f"⚠️ NAUTILUS - Erro ao parsear JSON: {parse_error}")
                
                success_result = {
                    'success': True,
                    'message': 'Dados do usuário enviados para Nautilus com sucesso',
                    'nautilus_response': nautilus_response_data,
                    'nautilus_user_created_id': nautilus_response_data.get('id') if nautilus_response_data else None
                }
                
                print("✅ NAUTILUS - Retornando SUCESSO para o endpoint")
                print(f"📦 NAUTILUS - Resultado: {success_result}")
                print("=" * 80)
                
                return success_result
            
            elif response.status_code == 400:
                # Analisar erro 400 específico
                response_text = response.text.strip('"')
                print(f"⚠️ NAUTILUS - Erro 400 detectado: {response_text}")
                
                # Verificar se é erro de duplicata
                if 'SequelizeUniqueConstraintError' in response_text or 'Validation error' in response_text:
                    
                    # Identificar qual campo está duplicado
                    error_details = "Dados já existem no sistema Nautilus"
                    if 'email' in response_text.lower():
                        error_details += " - Email já cadastrado"
                    elif 'apikey' in response_text.lower() or 'api' in response_text.lower():
                        error_details += " - Credenciais API da Bitget já cadastradas"
                    
                    print(f"🚫 NAUTILUS - Erro de duplicata: {error_details}")
                    
                    error_result = {
                        'success': False,
                        'error': error_details,
                        'error_type': 'duplicate_data',
                        'details': response_text,
                        'user_message': 'Este email ou suas credenciais da Bitget já estão cadastrados no sistema. Se você já possui uma conta, faça login.'
                    }
                    
                    print(f"❌ NAUTILUS - Retornando ERRO de duplicata")
                    print(f"📦 NAUTILUS - Resultado: {error_result}")
                    print("=" * 80)
                    
                    return error_result
                else:
                    # Outros erros de validação
                    print(f"❌ NAUTILUS - Erro de validação: {response_text}")
                    
                    validation_result = {
                        'success': False,
                        'error': f'Erro de validação no Nautilus: {response_text}',
                        'error_type': 'validation_error',
                        'details': response_text
                    }
                    
                    print(f"❌ NAUTILUS - Retornando ERRO de validação")
                    print(f"📦 NAUTILUS - Resultado: {validation_result}")
                    print("=" * 80)
                    
                    return validation_result
            
            else:
                # Outros códigos de erro HTTP
                print(f"❌ NAUTILUS - Erro HTTP {response.status_code}: {response.text}")
                
                http_error_result = {
                    'success': False,
                    'error': f'Falha ao enviar dados para Nautilus: HTTP {response.status_code}',
                    'details': response.text,
                    'response_headers': dict(response.headers)
                }
                
                print(f"❌ NAUTILUS - Retornando ERRO HTTP")
                print(f"📦 NAUTILUS - Resultado: {http_error_result}")
                print("=" * 80)
                
                return http_error_result
                
        except requests.exceptions.Timeout:
            print("⏱️ NAUTILUS - Timeout na requisição")
            timeout_result = {
                'success': False,
                'error': 'Timeout na comunicação com o servidor Nautilus',
                'error_type': 'timeout'
            }
            print("=" * 80)
            return timeout_result
            
        except requests.exceptions.ConnectionError:
            print("🔌 NAUTILUS - Erro de conexão")
            connection_result = {
                'success': False,
                'error': 'Falha na conexão com o servidor Nautilus',
                'error_type': 'connection_error'
            }
            print("=" * 80)
            return connection_result
            
        except Exception as e:
            print(f"💥 NAUTILUS - Erro inesperado: {str(e)}")
            exception_result = {
                'success': False,
                'error': f'Erro inesperado ao conectar com Nautilus: {str(e)}',
                'error_type': 'unexpected_error'
            }
            print("=" * 80)
            return exception_result
    
    def register_user_in_nautilus(self, user_data):
        """
        Registra um usuário no sistema Nautilus (método legado - mantido para compatibilidade)
        Agora apenas obtém as credenciais do Nautilus
        
        Args:
            user_data (dict): Dados do usuário para registro
        
        Returns:
            dict: Resultado do registro
        """
        # Por enquanto, apenas obtém as credenciais do Nautilus
        # Futuramente pode ser expandido para enviar dados do usuário
        return self.get_nautilus_credentials()
    
    def sync_user_data(self, user_email, trade_data=None):
        """
        Sincroniza dados do usuário com o Nautilus
        
        Args:
            user_email (str): Email do usuário
            trade_data (dict, optional): Dados de trade para sincronização
        
        Returns:
            dict: Resultado da sincronização
        """
        # Garantir autenticação
        auth_result = self.ensure_authenticated()
        if not auth_result['success']:
            return auth_result
        
        try:
            url = f"{self.base_url}/api/users/sync"
            
            sync_data = {
                "email": user_email,
                "platform": "BitNova",
                "sync_timestamp": datetime.now().isoformat()
            }
            
            if trade_data:
                sync_data["trade_data"] = trade_data
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            
            response = requests.post(
                url,
                json=sync_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Dados sincronizados com sucesso',
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Sync failed: HTTP {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Sync error: {str(e)}'
            }

# Instância global do serviço
nautilus_service = NautilusService()