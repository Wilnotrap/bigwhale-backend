# backend/api/bitget_client.py
import requests
import hmac
import hashlib
import base64
import time
import json
from urllib.parse import urlencode

class BitgetAPI:
    """Cliente para interagir com a API da Bitget"""
    
    def __init__(self, api_key, secret_key, passphrase=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://api.bitget.com"
        
    def _generate_signature(self, timestamp, method, request_path, body=""):
        """Gera assinatura para autenticação na API Bitget"""
        # Split path and query string if present
        if '?' in request_path:
            path_parts = request_path.split('?', 1)
            path = path_parts[0]
            query_string = path_parts[1]
            # According to Bitget docs: timestamp + method + requestPath + "?" + queryString + body
            message = timestamp + method.upper() + path + '?' + query_string + body
        else:
            # No query string: timestamp + method + requestPath + body
            message = timestamp + method.upper() + request_path + body
            
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature
    
    def _get_headers(self, timestamp, method, request_path, body=""):
        """Gera headers para requisições autenticadas"""
        signature = self._generate_signature(timestamp, method, request_path, body)
        headers = {
            'ACCESS-KEY': self.api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        if self.passphrase:
            headers['ACCESS-PASSPHRASE'] = self.passphrase
        return headers
    
    def _send_request(self, method, endpoint, params=None, data=None):
        """Envia requisição para a API da Bitget"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir query string se houver parâmetros
            query_string = ''
            if params:
                # Remover parâmetros None ou vazios
                params = {k: v for k, v in params.items() if v is not None}
                if params:
                    query_string = '?' + urlencode(params)
            
            request_path = endpoint + query_string
            
            # Preparar body se houver dados
            body = ''
            if data:
                body = json.dumps(data)
            
            # Gerar headers
            headers = self._get_headers(timestamp, method, request_path, body)
            
            # Fazer requisição
            url = self.base_url + request_path
            print(f"[BitgetAPI] Enviando requisição {method} para {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=30
            )
            
            print(f"[BitgetAPI] Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[BitgetAPI] Resposta: {json.dumps(response_data, indent=2)}")
                return response_data
            else:
                print(f"[BitgetAPI] Erro na requisição: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[BitgetAPI] Exceção ao enviar requisição: {e}")
            return None
    
    def validate_credentials(self):
        """Valida as credenciais da API fazendo uma chamada de teste"""
        try:
            timestamp = str(int(time.time() * 1000))
            request_path = "/api/spot/v1/account/assets"
            method = "GET"
            
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                is_valid = data.get('code') == '00000' or 'data' in data
                return is_valid
            else:
                return False
                
        except Exception as e:
            print(f"Erro ao validar credenciais: {e}")
            return False
    
    def get_account_balance(self):
        """Obtém o saldo da conta"""
        return self._send_request('GET', '/api/spot/v1/account/assets')
    
    def get_futures_positions(self, product_type="USDT-FUTURES", margin_coin=None):
        """Obtém posições de futuros"""
        params = {'productType': product_type}
        if margin_coin:
            params['marginCoin'] = margin_coin
        return self._send_request('GET', '/api/mix/v1/position/allPosition', params=params)
    
    def get_futures_balance(self, product_type="USDT-FUTURES", margin_coin="USDT"):
        """Obtém saldo de futuros"""
        params = {
            'productType': product_type,
            'marginCoin': margin_coin
        }
        return self._send_request('GET', '/api/mix/v1/account/account', params=params)