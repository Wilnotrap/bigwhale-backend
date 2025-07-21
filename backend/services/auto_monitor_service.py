# backend/services/auto_monitor_service.py
import threading
import time
import logging
from datetime import datetime
from models.active_signal import ActiveSignal
from database import db
from utils.security import decrypt_api_key
from api.bitget_client import BitgetAPI
from models.user import User

class AutoMonitorService:
    """
    Serviço de monitoramento automático de alvos
    Roda em background verificando alvos a cada minuto
    """
    
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Inicia o monitoramento automático"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            self.logger.info("🤖 Monitoramento automático iniciado")
    
    def stop(self):
        """Para o monitoramento automático"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("🛑 Monitoramento automático parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                with self.app.app_context():
                    self._check_all_signals()
                
                # Aguardar 60 segundos (1 minuto)
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento automático: {e}")
                time.sleep(30)  # Aguardar menos tempo em caso de erro
    
    def _check_all_signals(self):
        """Verifica todos os sinais ativos de todos os usuários"""
        try:
            # Buscar todos os sinais ativos com tratamento de erro
            try:
                active_signals = ActiveSignal.query.filter_by(status='active').all()
            except Exception as db_error:
                self.logger.error(f"Erro ao buscar sinais do banco: {db_error}")
                # Tentar limpar dados corrompidos
                self._clean_corrupted_data()
                return
            
            if not active_signals:
                return
            
            self.logger.info(f"🔍 Verificando {len(active_signals)} sinais ativos")
            
            # Agrupar sinais por usuário para otimizar chamadas da API
            signals_by_user = {}
            for signal in active_signals:
                try:
                    # Verificar se o sinal é válido
                    if not self._is_signal_valid(signal):
                        continue
                        
                    user_id = signal.user_id
                    if user_id not in signals_by_user:
                        signals_by_user[user_id] = []
                    signals_by_user[user_id].append(signal)
                except Exception as e:
                    self.logger.error(f"Erro ao processar sinal {signal.id}: {e}")
                    continue
            
            # Processar cada usuário
            for user_id, user_signals in signals_by_user.items():
                self._check_user_signals(user_id, user_signals)
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar sinais: {e}")
    
    def _is_signal_valid(self, signal):
        """Verifica se um sinal é válido"""
        try:
            # Verificar campos essenciais
            if not signal.symbol or not signal.side:
                return False
            
            # Verificar se targets é válido
            try:
                targets = signal.targets
                if not isinstance(targets, list):
                    return False
            except:
                return False
            
            # Verificar se entry_price é válido
            if not signal.entry_price or signal.entry_price <= 0:
                return False
            
            return True
        except:
            return False
    
    def _clean_corrupted_data(self):
        """Limpa dados corrompidos do banco"""
        try:
            self.logger.info("🧹 Limpando dados corrompidos...")
            
            # Buscar todos os sinais
            all_signals = ActiveSignal.query.all()
            corrupted_count = 0
            
            for signal in all_signals:
                try:
                    # Testar se o sinal é válido
                    if not self._is_signal_valid(signal):
                        db.session.delete(signal)
                        corrupted_count += 1
                except:
                    # Se não consegue processar, remover
                    db.session.delete(signal)
                    corrupted_count += 1
            
            if corrupted_count > 0:
                db.session.commit()
                self.logger.info(f"🧹 {corrupted_count} sinais corrompidos removidos")
                
        except Exception as e:
            self.logger.error(f"Erro ao limpar dados corrompidos: {e}")
    
    def _check_user_signals(self, user_id, signals):
        """Verifica sinais de um usuário específico"""
        try:
            user = User.query.get(user_id)
            if not user:
                return
            
            # Verificar se tem credenciais da API
            if not user.bitget_api_key_encrypted or not user.bitget_api_secret_encrypted:
                return
            
            # Descriptografar credenciais
            api_key = decrypt_api_key(user.bitget_api_key_encrypted)
            api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
            passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
            
            if not api_key or not api_secret:
                return
            
            # Criar cliente Bitget
            bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
            
            # Buscar posições abertas
            positions_response = bitget_client.get_all_positions()
            if not positions_response or positions_response.get('code') != '00000':
                return
            
            positions_data = positions_response.get('data', [])
            
            # Criar dicionário de preços atuais
            current_prices = {}
            for position in positions_data:
                total_size = float(position.get('total', 0))
                if total_size > 0:  # Apenas posições realmente abertas
                    symbol = position.get('symbol')
                    mark_price = float(position.get('markPrice', 0))
                    if symbol and mark_price > 0:
                        current_prices[symbol] = mark_price
            
            # Verificar cada sinal
            updates_made = 0
            for signal in signals:
                try:
                    current_price = current_prices.get(signal.symbol)
                    
                    if current_price:
                        # Atualizar alvos atingidos
                        if signal.update_targets_hit(current_price):
                            updates_made += 1
                            self.logger.info(f"🎯 {signal.symbol}: {signal.targets_hit} alvos atingidos (preço: ${current_price:.4f})")
                    else:
                        # Se não há posição aberta, buscar preço via ticker
                        try:
                            ticker_response = bitget_client.get_ticker(signal.symbol)
                            if ticker_response and ticker_response.get('code') == '00000':
                                ticker_data = ticker_response.get('data')
                                if ticker_data:
                                    current_price = float(ticker_data.get('lastPr', 0))
                                    if current_price > 0:
                                        if signal.update_targets_hit(current_price):
                                            updates_made += 1
                                            self.logger.info(f"🎯 {signal.symbol}: {signal.targets_hit} alvos atingidos (ticker: ${current_price:.4f})")
                        except:
                            pass
                except Exception as e:
                    self.logger.error(f"Erro ao verificar sinal {signal.id}: {e}")
                    continue
            
            # Salvar atualizações no banco
            if updates_made > 0:
                try:
                    db.session.commit()
                    self.logger.info(f"💾 {updates_made} sinais atualizados para usuário {user_id}")
                except Exception as e:
                    self.logger.error(f"Erro ao salvar atualizações: {e}")
                    db.session.rollback()
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar sinais do usuário {user_id}: {e}")
    
    def force_check_all(self):
        """Força uma verificação imediata de todos os sinais"""
        try:
            with self.app.app_context():
                self.logger.info("🔄 Verificação forçada iniciada")
                self._check_all_signals()
                self.logger.info("✅ Verificação forçada concluída")
                return True
        except Exception as e:
            self.logger.error(f"Erro na verificação forçada: {e}")
            return False

# Instância global do serviço
auto_monitor = None

def init_auto_monitor(app):
    """Inicializa o serviço de monitoramento automático"""
    global auto_monitor
    auto_monitor = AutoMonitorService(app)
    auto_monitor.start()
    return auto_monitor

def get_auto_monitor():
    """Retorna a instância do monitoramento automático"""
    return auto_monitor