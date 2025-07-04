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
        """
        Envia requisição para a API da Bitget
        """
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
        """Valida as credenciais da API fazendo uma chamada de teste com diagnóstico detalhado"""
        try:
            print(f"🔍 Validando credenciais da API Bitget...")
            
            # Verificações básicas das credenciais
            if not self.api_key or not self.secret_key:
                print(f"❌ Credenciais incompletas: API Key: {bool(self.api_key)}, Secret: {bool(self.secret_key)}, Passphrase: {bool(self.passphrase)}")
                return False
                
            # Verificar formato básico das credenciais
            if not self.api_key.startswith('bg_'):
                print(f"⚠️ API Key não parece ter formato Bitget válido (deve começar com 'bg_'): {self.api_key[:10]}...")
                
            print(f"📊 Testando credenciais com API Key: {self.api_key[:10]}...")
            
            # Tenta obter informações da conta para validar as credenciais
            timestamp = str(int(time.time() * 1000))
            request_path = "/api/spot/v1/account/assets"
            method = "GET"
            
            print(f"🌐 Fazendo requisição para: {self.base_url + request_path}")
            headers = self._get_headers(timestamp, method, request_path)
            print(f"📋 Headers preparados (sem mostrar assinatura)")
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=10
            )
            
            print(f"📡 Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Resposta recebida: {json.dumps(data, indent=2)}")
                
                # Verifica se a resposta contém dados válidos
                is_valid = data.get('code') == '00000' or 'data' in data
                if is_valid:
                    print("✅ Credenciais da API Bitget válidas.")
                else:
                    print(f"❌ Credenciais inválidas - código de resposta: {data.get('code')}")
                return is_valid
            else:
                response_text = response.text
                print(f"❌ Erro na validação: {response.status_code} - {response_text}")
                
                # Análise específica de erros comuns
                try:
                    error_data = response.json()
                    error_code = error_data.get('code')
                    error_msg = error_data.get('msg', '')
                    
                    if error_code == '40037':
                        print("🔑 DIAGNÓSTICO: API Key não existe ou está incorreta")
                        print("💡 SOLUÇÃO: Verifique se copiou a API Key corretamente da Bitget")
                    elif error_code == '40038':
                        print("🔐 DIAGNÓSTICO: Secret Key está incorreto")
                        print("💡 SOLUÇÃO: Verifique se copiou o Secret Key corretamente")
                    elif error_code == '40710':
                        print("🚫 DIAGNÓSTICO: Status da conta anormal")
                        print("💡 SOLUÇÃO: Sua conta Bitget pode estar bloqueada ou com restrições")
                    elif error_code == '40103':
                        print("🔒 DIAGNÓSTICO: Passphrase incorreta")
                        print("💡 SOLUÇÃO: Verifique se o passphrase está correto")
                    elif error_code == '40104':
                        print("🕐 DIAGNÓSTICO: Timestamp da requisição inválido")
                        print("💡 SOLUÇÃO: Problema de sincronização de horário")
                    elif error_code == '40105':
                        print("🔏 DIAGNÓSTICO: Assinatura inválida")
                        print("💡 SOLUÇÃO: Problema na geração da assinatura - verifique todas as credenciais")
                    elif 'permission' in error_msg.lower():
                        print("🛡️ DIAGNÓSTICO: Permissões insuficientes")
                        print("💡 SOLUÇÃO: A API Key precisa de permissões de 'Read' no mínimo")
                        print("🔧 CONFIGURAR: Acesse Bitget > API Management > Edit API > Enable 'Read' permissions")
                    else:
                        print(f"❓ DIAGNÓSTICO: Erro não identificado - Código: {error_code}, Mensagem: {error_msg}")
                        
                except Exception as json_error:
                    print(f"❌ Erro ao processar resposta JSON: {json_error}")
                    
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ DIAGNÓSTICO: Timeout na conexão com a API Bitget")
            print("💡 SOLUÇÃO: Verifique sua conexão com a internet")
            return False
        except requests.exceptions.ConnectionError:
            print("🌐 DIAGNÓSTICO: Erro de conexão com a API Bitget")
            print("💡 SOLUÇÃO: Verifique sua conexão com a internet ou se a API da Bitget está funcionando")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao validar credenciais: {e}")
            return False
    
    def get_account_balance(self):
        """Obtém o saldo da conta"""
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
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao obter saldo: {e}")
            return None
    
    def get_futures_positions(self, product_type="USDT-FUTURES", margin_coin=None):
        """Obtém posições de futuros usando API v2"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir parâmetros de query
            params = {'productType': product_type}
            if margin_coin:
                params['marginCoin'] = margin_coin
            
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/position/all-position?{query_string}"
            method = "GET"
            
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao obter posições: {e}")
            return None
    
    def get_order_history(self, product_type="USDT-FUTURES", symbol=None, limit=100, start_time=None, end_time=None, cursor=None):
        """Obtém histórico de ordens usando API v2"""
        try:
            timestamp = str(int(time.time() * 1000))
            params = {
                'productType': product_type,
                'limit': str(limit)
            }
            if symbol:
                params['symbol'] = symbol
            if start_time:
                params['startTime'] = str(start_time)
            if end_time:
                params['endTime'] = str(end_time)
            if cursor: # Adicionado para suportar paginação, se aplicável
                params['cursor'] = cursor
                
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/order/orders-history?{query_string}"
            method = "GET"
            
            print(f"[BitgetAPI] Chamando get_order_history com path: {request_path}") # Log dos parâmetros
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=15 # Aumentado timeout para histórico
            )
            
            response_data = response.json()
            print(f"[BitgetAPI] Resposta de get_order_history (status {response.status_code}): {json.dumps(response_data, indent=2)}") # Log da resposta crua

            if response.status_code == 200:
                return response_data
            else:
                print(f"[BitgetAPI] Erro HTTP em get_order_history: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[BitgetAPI] Exceção em get_order_history: {e}")
            return None
    
    def get_history_orders(self, **kwargs):
        """
        Busca o histórico de ordens fechadas
        """
        endpoint = '/api/mix/v1/order/history'
        params = {
            'symbol': kwargs.get('symbol'),
            'startTime': kwargs.get('start_time'),
            'endTime': kwargs.get('end_time'),
            'limit': kwargs.get('limit', 100)
        }
        return self._send_request('GET', endpoint, params)
    
    def get_closed_positions_history(self, product_type="USDT-FUTURES", symbol=None, limit=100, start_time=None, end_time=None):
        """
        Busca o histórico de posições fechadas usando a API v2
        """
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir parâmetros de query
            params = {
                'productType': product_type,
                'pageSize': str(limit)
            }
            
            if symbol:
                params['symbol'] = symbol
            if start_time:
                params['startTime'] = str(start_time)
            if end_time:
                params['endTime'] = str(end_time)
                
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/position/history-position?{query_string}"
            method = "GET"
            
            print(f"[BitgetAPI] Chamando get_closed_positions_history com path: {request_path}")
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=15
            )
            
            response_data = response.json()
            print(f"[BitgetAPI] Resposta de get_closed_positions_history (status {response.status_code}): {json.dumps(response_data, indent=2)}")

            if response.status_code == 200:
                return response_data
            else:
                print(f"[BitgetAPI] Erro HTTP em get_closed_positions_history: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[BitgetAPI] Exceção em get_closed_positions_history: {e}")
            return None
    
    def get_orders_history(self, product_type="USDT-FUTURES", symbol=None, limit=100, start_time=None, end_time=None):
        """
        Busca o histórico de ordens usando a API v2 (inclui campo leverage)
        """
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir parâmetros de query
            params = {
                'productType': product_type,
                'limit': str(limit)
            }
            
            if symbol:
                params['symbol'] = symbol
            if start_time:
                params['startTime'] = str(start_time)
            if end_time:
                params['endTime'] = str(end_time)
                
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/order/orders-history?{query_string}"
            method = "GET"
            
            print(f"[BitgetAPI] Chamando get_orders_history com path: {request_path}")
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=15
            )
            
            response_data = response.json()
            print(f"[BitgetAPI] Resposta de get_orders_history (status {response.status_code}): {json.dumps(response_data, indent=2)}")

            if response.status_code == 200:
                return response_data
            else:
                print(f"[BitgetAPI] Erro HTTP em get_orders_history: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[BitgetAPI] Exceção em get_orders_history: {e}")
            return None

    def get_futures_balance(self, product_type="USDT-FUTURES", margin_coin="USDT"):
        """Obtém saldo da conta de futuros usando API v2"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir parâmetros de query
            params = {'productType': product_type}
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/account/accounts?{query_string}"
            method = "GET"
            
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao obter saldo de futuros: {e}")
            return None
    
    def get_all_positions(self, product_type="USDT-FUTURES", margin_coin=None):
        """Obtém todas as posições atuais usando endpoint all-position que fornece dados completos incluindo leverage"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir parâmetros de query
            params = {'productType': product_type}
            if margin_coin:
                params['marginCoin'] = margin_coin
                
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/position/all-position?{query_string}"
            method = "GET"
            
            print(f"[BitgetAPI] Chamando get_all_positions com path: {request_path}")
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=15
            )
            
            response_data = response.json()
            print(f"[BitgetAPI] Resposta de get_all_positions (status {response.status_code}): {json.dumps(response_data, indent=2)}")

            if response.status_code == 200:
                return response_data
            else:
                print(f"[BitgetAPI] Erro HTTP em get_all_positions: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[BitgetAPI] Exceção em get_all_positions: {e}")
            return None
    
    def get_margin_for_symbol(self, symbol, product_type="USDT-FUTURES"):
        """
        Busca dados de margem específicos para um símbolo usando o endpoint all-position
        Útil para obter dados de margem que não estão disponíveis no histórico
        """
        try:
            print(f"[BitgetAPI] Buscando margem para símbolo: {symbol}")
            
            # Buscar todas as posições atuais
            all_positions_response = self.get_all_positions(product_type=product_type)
            
            if not all_positions_response or all_positions_response.get('code') != '00000':
                print(f"[BitgetAPI] Erro ao buscar posições para margem: {all_positions_response}")
                return None
                
            positions = all_positions_response.get('data', [])
            
            # Procurar pela posição específica do símbolo
            for position in positions:
                if position.get('symbol') == symbol:
                    margin_size = position.get('marginSize')
                    if margin_size and float(margin_size) > 0:
                        print(f"[BitgetAPI] Margem encontrada para {symbol}: {margin_size}")
                        return {
                            'symbol': symbol,
                            'marginSize': float(margin_size),
                            'marginCoin': position.get('marginCoin'),
                            'leverage': position.get('leverage'),
                            'holdSide': position.get('holdSide'),
                            'source': 'all-position'
                        }
                    else:
                        print(f"[BitgetAPI] Posição encontrada para {symbol}, mas sem margem ativa")
                        return None
            
            print(f"[BitgetAPI] Nenhuma posição ativa encontrada para {symbol}")
            return None
            
        except Exception as e:
            print(f"[BitgetAPI] Erro ao buscar margem para {symbol}: {e}")
            return None

    def get_position_history(self, product_type="USDT-FUTURES", symbol=None, limit=100, start_time=None, end_time=None):
        """Obtém histórico de posições fechadas usando endpoint específico para posições"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir parâmetros de query
            params = {
                'productType': product_type,
                'pageSize': str(limit)
            }
            
            if symbol:
                params['symbol'] = symbol
            if start_time:
                params['startTime'] = str(start_time)
            if end_time:
                params['endTime'] = str(end_time)
                
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/position/history-position?{query_string}"
            method = "GET"
            
            print(f"[BitgetAPI] Chamando get_position_history com path: {request_path}")
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=15
            )
            
            response_data = response.json()
            print(f"[BitgetAPI] Resposta de get_position_history (status {response.status_code}): {json.dumps(response_data, indent=2)}")

            if response.status_code == 200:
                return response_data
            else:
                print(f"[BitgetAPI] Erro HTTP em get_position_history: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[BitgetAPI] Exceção em get_position_history: {e}")
            return None

    def flash_close_position(self, symbol, hold_side=None, product_type="USDT-FUTURES"):
        """Fecha posição usando flash close (market price)"""
        try:
            timestamp = str(int(time.time() * 1000))
            request_path = "/api/v2/mix/order/close-positions"
            method = "POST"
            
            # Corpo da requisição
            body_data = {
                "symbol": symbol,
                "productType": product_type
            }
            
            # Adicionar holdSide se especificado
            if hold_side:
                body_data["holdSide"] = hold_side
            
            body = json.dumps(body_data)
            
            headers = self._get_headers(timestamp, method, request_path, body)
            
            print(f"[BitgetAPI] Flash close position - Symbol: {symbol}, HoldSide: {hold_side}")
            
            response = requests.post(
                self.base_url + request_path,
                headers=headers,
                data=body,
                timeout=30
            )
            
            print(f"[BitgetAPI] Flash close response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[BitgetAPI] Flash close response: {json.dumps(response_data, indent=2)}")
                return response_data
            else:
                print(f"[BitgetAPI] Erro ao fechar posição: {response.status_code} - {response.text}")
                return {
                    'code': str(response.status_code),
                    'msg': response.text,
                    'success': False
                }
                
        except Exception as e:
            print(f"[BitgetAPI] Exceção ao fechar posição: {e}")
            return {
                'code': '500',
                'msg': str(e),
                'success': False
            }
    
    def get_fills_history(self, product_type="USDT-FUTURES", symbol=None, limit=100, start_time=None, end_time=None):
        """Obtém histórico de execuções (fills) para identificar trades fechados"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Construir parâmetros de query
            params = {
                'productType': product_type,
                'pageSize': str(limit)
            }
            
            if symbol:
                params['symbol'] = symbol
            if start_time:
                params['startTime'] = str(start_time)
            if end_time:
                params['endTime'] = str(end_time)
                
            query_string = urlencode(params)
            request_path = f"/api/v2/mix/order/fills?{query_string}"
            method = "GET"
            
            headers = self._get_headers(timestamp, method, request_path)
            
            response = requests.get(
                self.base_url + request_path,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Erro ao obter histórico de execuções: {e}")
            return None
    
    def get_ticker(self, symbol):
        """Obtém informações do ticker (preço atual) de um símbolo"""
        try:
            # Primeiro tentar endpoint específico com formato de futuros
            try:
                response = requests.get(
                    f"{self.base_url}/api/v2/mix/market/ticker?symbol={symbol}",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == '00000':
                        return data
            except Exception:
                pass
            
            # Fallback: usar endpoint de todos os tickers e filtrar
            response = requests.get(
                f"{self.base_url}/api/v2/mix/market/tickers?productType=USDT-FUTURES",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '00000' and data.get('data'):
                    # Procurar o símbolo específico
                    for ticker in data['data']:
                        if ticker.get('symbol') == symbol:
                            return {
                                'code': '00000',
                                'data': [ticker]
                            }
                    
                    # Se não encontrar exato, tentar variações
                    for ticker in data['data']:
                        symbol_variants = [symbol, f"{symbol}_UMCBL", f"{symbol}PERP"]
                        if ticker.get('symbol') in symbol_variants:
                            return {
                                'code': '00000',
                                'data': [ticker]
                            }
                            
            print(f"Símbolo {symbol} não encontrado nos tickers")
            return None
                
        except Exception as e:
            print(f"Erro ao obter ticker para {symbol}: {e}")
            return None

    def get_usd_brl_rate(self):
        """Obtém a taxa de câmbio USD/BRL usando APIs públicas confiáveis"""
        try:
            # Método 1: Tentar ExchangeRate API (gratuita e confiável)
            try:
                response = requests.get(
                    "https://api.exchangerate-api.com/v4/latest/USD",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    brl_rate = data.get('rates', {}).get('BRL')
                    if brl_rate and brl_rate > 0:
                        print(f"[BitgetAPI] Taxa USD/BRL obtida da ExchangeRate API: {brl_rate:.4f}")
                        return float(brl_rate)
            except Exception as e:
                print(f"[BitgetAPI] Erro na ExchangeRate API: {e}")
            
            # Método 2: Tentar API do Banco Central do Brasil (oficial)
            try:
                response = requests.get(
                    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        brl_rate = float(data[0].get('valor', 0))
                        if brl_rate > 0:
                            print(f"[BitgetAPI] Taxa USD/BRL obtida do Banco Central: {brl_rate:.4f}")
                            return brl_rate
            except Exception as e:
                print(f"[BitgetAPI] Erro na API do Banco Central: {e}")
            
            # Método 3: Tentar Bitget (caso tenham algum par relacionado)
            try:
                # Verificar se existe BRLUSDT na Bitget
                response = requests.get(
                    f"{self.base_url}/api/v2/spot/market/tickers?symbol=BRLUSDT",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == '00000' and data.get('data'):
                        ticker_data = data['data'][0]
                        brl_usd_rate = float(ticker_data.get('lastPr', 0))
                        if brl_usd_rate > 0:
                            # Se for BRLUSDT, inverter para obter USDBRL
                            usd_brl_rate = 1 / brl_usd_rate
                            print(f"[BitgetAPI] Taxa USD/BRL calculada da Bitget BRLUSDT: {usd_brl_rate:.4f}")
                            return usd_brl_rate
            except Exception as e:
                print(f"[BitgetAPI] Erro ao verificar Bitget BRLUSDT: {e}")
            
            print("[BitgetAPI] Todas as APIs de cotação falharam")
            return None
                
        except Exception as e:
            print(f"[BitgetAPI] Erro geral ao obter taxa USD/BRL: {e}")
            return None

    def get_market_price(self, symbol):
        """Obtém o preço de mercado atual para um símbolo específico."""
        ticker_data = self.get_ticker(symbol)
        if ticker_data and 'data' in ticker_data and ticker_data['data']:
             # Para futuros, a lista pode conter mais de um item, mas geralmente o primeiro é o correto
            if isinstance(ticker_data['data'], list) and len(ticker_data['data']) > 0:
                return float(ticker_data['data'][0].get('lastPr'))
            # Para spot, a estrutura pode ser diferente
            elif isinstance(ticker_data['data'], dict):
                 return float(ticker_data['data'].get('lastPr'))
        return None