# backend/websocket/bitget_ws.py
import asyncio
import websockets
import json
import hmac
import hashlib
import base64
import time
from threading import Thread
import logging

class BitgetWebSocket:
    """Cliente WebSocket para a API da Bitget"""
    
    def __init__(self, api_key=None, secret_key=None, passphrase=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.ws_url = "wss://ws.bitget.com/v2/ws/public"
        self.websocket = None
        self.subscriptions = set()
        self.callbacks = {}
        self.running = False
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _generate_signature(self, timestamp, method, request_path, body=""):
        """Gera assinatura para autenticação WebSocket"""
        if not self.secret_key:
            return None
        
        message = timestamp + method.upper() + request_path + body
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature
    
    def _create_auth_message(self):
        """Cria mensagem de autenticação"""
        if not self.api_key or not self.secret_key:
            return None
        
        timestamp = str(int(time.time()))
        sign = self._generate_signature(timestamp, "GET", "/user/verify", "")
        
        auth_message = {
            "op": "login",
            "args": [{
                "apiKey": self.api_key,
                "passphrase": self.passphrase or "",
                "timestamp": timestamp,
                "sign": sign
            }]
        }
        return auth_message
    
    async def connect(self):
        """Conecta ao WebSocket da Bitget"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.running = True
            self.logger.info("Conectado ao WebSocket da Bitget")
            
            # Autenticar se as credenciais estiverem disponíveis
            if self.api_key and self.secret_key:
                auth_message = self._create_auth_message()
                if auth_message:
                    await self.websocket.send(json.dumps(auth_message))
                    self.logger.info("Mensagem de autenticação enviada")
            
            return True
        except Exception as e:
            self.logger.error(f"Erro ao conectar: {e}")
            return False
    
    async def disconnect(self):
        """Desconecta do WebSocket"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            self.logger.info("Desconectado do WebSocket")
    
    async def subscribe_ticker(self, symbol, callback=None):
        """Inscreve-se para receber dados de ticker de um símbolo"""
        channel = f"ticker.{symbol}"
        
        subscribe_message = {
            "op": "subscribe",
            "args": [{
                "instType": "USDT-FUTURES",
                "channel": "ticker",
                "instId": symbol
            }]
        }
        
        if callback:
            self.callbacks[channel] = callback
        
        await self.websocket.send(json.dumps(subscribe_message))
        self.subscriptions.add(channel)
        self.logger.info(f"Inscrito no ticker de {symbol}")
    
    async def listen(self):
        """Escuta mensagens do WebSocket"""
        try:
            while self.running and self.websocket:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Log detalhado para debug
                self.logger.info(f"Mensagem completa recebida: {data}")
                
                # Processar diferentes tipos de mensagem
                if 'event' in data:
                    # Mensagem de evento (login, subscribe, etc.)
                    self.logger.info(f"Evento recebido: {data}")
                elif 'action' in data and data.get('action') in ['snapshot', 'update']:
                    # Dados de mercado no formato v2
                    await self._handle_market_data(data)
                elif 'arg' in data and 'data' in data:
                    # Dados de mercado no formato v1 (fallback)
                    await self._handle_market_data(data)
                elif data.get('event') == 'pong' or message == 'pong':
                    # Resposta ao ping
                    self.logger.debug("Pong recebido")
                else:
                    self.logger.info(f"Mensagem não reconhecida: {data}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Conexão WebSocket fechada")
        except Exception as e:
            self.logger.error(f"Erro ao escutar WebSocket: {e}")
    
    async def _handle_market_data(self, data):
        """Processa dados de mercado recebidos"""
        try:
            arg = data.get('arg', {})
            channel = arg.get('channel')
            inst_id = arg.get('instId')
            
            # Criar chave do callback
            if channel == 'ticker':
                callback_key = f"ticker.{inst_id}"
            elif channel == 'books':
                callback_key = f"books.{inst_id}"
            else:
                callback_key = channel
            
            # Executar callback se existir
            if callback_key in self.callbacks:
                await self.callbacks[callback_key](data)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar dados de mercado: {e}")
    
    def start_in_thread(self):
        """Inicia o WebSocket em uma thread separada"""
        def run_websocket():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def main():
                await self.connect()
                await self.listen()
            
            loop.run_until_complete(main())
        
        thread = Thread(target=run_websocket, daemon=True)
        thread.start()
        return thread