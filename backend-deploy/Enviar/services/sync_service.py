import time
import threading
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import current_app
from models.user import User
from models.trade import Trade
from api.bitget_client import BitgetAPI
from utils.security import decrypt_api_key
from database import db
import logging
import json

# Variáveis globais para controle da sincronização
sync_active = False
active_syncs = set()

class AutoSyncService:
    """Serviço de sincronização automática de trades"""
    
    def __init__(self, app=None, sync_interval=60):  # 1 minuto por padrão
        self.app = app
        self.sync_interval = sync_interval
        self.running = False
        self.thread = None
        
    def start(self):
        """Inicia o serviço de sincronização automática"""
        global sync_active
        if not self.running:
            self.running = True
            sync_active = True
            self.thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.thread.start()
            print(f"Serviço de sincronização automática iniciado (intervalo: {self.sync_interval}s)")
    
    def stop(self):
        """Para o serviço de sincronização automática"""
        global sync_active, active_syncs
        self.running = False
        sync_active = False
        active_syncs.clear()
        if self.thread:
            self.thread.join()
        print("Serviço de sincronização automática parado")
    
    def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.running:
            try:
                if self.app:
                    with self.app.app_context():
                        self._sync_all_users()
                else:
                    with current_app.app_context():
                        self._sync_all_users()
            except Exception as e:
                print(f"Erro na sincronização automática: {e}")
                # ADICIONAR: logging adequado
                logging.error(f"Sync error: {e}", exc_info=True)
            
            # Aguardar próximo ciclo
            time.sleep(self.sync_interval)
    
    def _sync_all_users(self):
        """Sincroniza trades de todos os usuários ativos"""
        try:
            # Buscar usuários com credenciais configuradas
            users = User.query.filter(
                User.bitget_api_key_encrypted.isnot(None),
                User.bitget_api_secret_encrypted.isnot(None),
                User.is_active == True
            ).all()
            
            # Sincronizar status Nautilus a cada 10 ciclos (10 minutos)
            if not hasattr(self, '_nautilus_sync_counter'):
                self._nautilus_sync_counter = 0
            
            self._nautilus_sync_counter += 1
            if self._nautilus_sync_counter >= 10:
                self._nautilus_sync_counter = 0
                try:
                    sync_nautilus_status_for_all_users()
                except Exception as e:
                    print(f"[AutoSync] Erro na sincronização Nautilus: {e}")
            
            for user in users:
                try:
                    self._sync_user_trades(user)
                except Exception as e:
                    print(f"Erro ao sincronizar usuário {user.id}: {e}")
                    
        except Exception as e:
            print(f"Erro ao buscar usuários para sincronização: {e}")
    
    def _sync_user_trades(self, user):
        """Sincroniza trades de um usuário específico"""
        global active_syncs
        active_syncs.add(user.id)
        updated_trades = 0
        closed_trades = 0
        new_trades = 0
        try:
            # Descriptografar credenciais da API
            api_key = decrypt_api_key(user.bitget_api_key_encrypted)
            api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
            passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
            
            if not api_key or not api_secret:
                print(f"Erro ao descriptografar credenciais do usuário {user.id}")
                return
            
            # Criar cliente Bitget
            bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
            
            # ATUALIZAÇÃO: Sincronizar saldo da conta de futuros
            try:
                balance_response = bitget_client.get_futures_balance(margin_coin="USDT")
                if balance_response and balance_response.get('code') == '00000':
                    balance_data = balance_response.get('data', [])
                    if balance_data:
                        # O saldo vem em uma lista, pegamos o primeiro item que corresponde a USDT
                        usdt_balance_info = next((item for item in balance_data if item.get('marginCoin') == 'USDT'), None)
                        if usdt_balance_info:
                            available_balance = float(usdt_balance_info.get('available', 0.0))
                            
                            # [CORREÇÃO] Desativado para não sobrescrever o saldo operacional com o da Bitget.
                            # O saldo da Bitget (futuros) não reflete o saldo operacional depositado.
                            # if user.operational_balance_usd != available_balance:
                            #     user.operational_balance_usd = available_balance
                            #     print(f"[SyncService] Saldo do usuário {user.id} atualizado para: {available_balance} USDT")
                                
            except Exception as e:
                print(f"[SyncService] Erro ao sincronizar saldo do usuário {user.id}: {e}")

            # Obter posições atuais (abertas)
            positions_response = bitget_client.get_futures_positions()
            if not positions_response or positions_response.get('code') != '00000':
                error_code = positions_response.get('code') if positions_response else 'NO_RESPONSE'
                error_msg = positions_response.get('msg') if positions_response else 'Sem resposta'
                
                # Se for erro de "Abnormal account status", pular este usuário temporariamente
                if error_code == '40710':
                    print(f"Usuário {user.id} com status de conta anormal (40710). Pulando sincronização.")
                    return
                
                print(f"Erro ao obter posições do usuário {user.id}: {error_code} - {error_msg}")
                return
            
            positions_data = positions_response.get('data', [])
            # updated_trades = 0 # Removed from here
            # closed_trades = 0 # Removed from here
            
            # Processar posições abertas
            current_open_positions = set()
            for position in positions_data:
                if float(position.get('total', 0)) == 0:
                    continue  # Pular posições vazias
                
                symbol = position.get('symbol')
                side = 'long' if position.get('holdSide') == 'long' else 'short'
                size = abs(float(position.get('total', 0)))
                entry_price = float(position.get('openPriceAvg', 0))
                unrealized_pnl = float(position.get('unrealizedPL', 0))
                leverage = float(position.get('leverage', 1.0))
                
                # Adicionar à lista de posições atualmente abertas
                current_open_positions.add((symbol, side))
                
                # Verificar se já existe um trade aberto para esta posição
                existing_trade = Trade.query.filter_by(
                    user_id=user.id,
                    symbol=symbol,
                    side=side,
                    status='open'
                ).first()
                
                if existing_trade:
                    # Atualizar trade existente apenas se houver mudanças significativas
                    # Converter pnl para float se for string
                    existing_pnl = existing_trade.pnl or 0
                    if isinstance(existing_pnl, str):
                        try:
                            existing_pnl = float(existing_pnl)
                        except (ValueError, TypeError):
                            existing_pnl = 0
                    
                    if (abs(existing_trade.size - size) > 0.001 or 
                        abs(existing_trade.entry_price - entry_price) > 0.001 or
                        abs(existing_pnl - unrealized_pnl) > 0.01 or
                        abs((existing_trade.leverage or 1.0) - leverage) > 0.001):
                        
                        existing_trade.size = size
                        existing_trade.entry_price = entry_price
                        existing_trade.pnl = unrealized_pnl
                        existing_trade.leverage = leverage
                        updated_trades += 1
                else:
                    # Criar novo trade se não existir
                    # PROTEÇÃO CONTRA DUPLICATAS INTELIGENTE: 
                    # Permitir múltiplas entradas no mesmo par com preços diferentes (aportes/novas entradas)
                    # Bloquear apenas trades idênticos (mesmo preço + tamanho + símbolo + lado) nos últimos 2 minutos
                    recent_check_time = datetime.utcnow() - timedelta(minutes=2)
                    
                    # Buscar trade duplicado EXATO (mesmo preço de entrada)
                    existing_duplicate = Trade.query.filter_by(
                        user_id=user.id,
                        symbol=symbol,
                        side=side,
                        size=size,
                        entry_price=entry_price  # CHAVE: Mesmo preço = duplicata real
                    ).filter(
                        Trade.opened_at >= recent_check_time,
                        Trade.status == 'open'
                    ).first()
                    
                    if existing_duplicate:
                        print(f"[SyncService] Trade duplicado EXATO detectado e ignorado: {symbol} ({side}) - Preço: {entry_price}, Tamanho: {size}")
                    else:
                        # Verificar se é uma nova entrada no mesmo par (aporte)
                        existing_same_pair = Trade.query.filter_by(
                            user_id=user.id,
                            symbol=symbol,
                            side=side,
                            status='open'
                        ).filter(Trade.entry_price != entry_price).first()
                        
                        if existing_same_pair:
                            print(f"[SyncService] Nova entrada/aporte detectado: {symbol} ({side}) - Preço anterior: {existing_same_pair.entry_price}, Novo preço: {entry_price}")
                        
                        new_trade = Trade(
                            user_id=user.id,
                            symbol=symbol,
                            side=side,
                            size=size,
                            entry_price=entry_price,
                            leverage=leverage,
                            status='open',
                            pnl=unrealized_pnl,
                            fees=0.0  # Definir valor padrão para fees
                        )
                        db.session.add(new_trade)
                        new_trades += 1
                        print(f"[SyncService] Novo trade criado: {symbol} ({side}) - Preço: {entry_price}, Tamanho: {size}")
            
            # Verificar trades que foram fechados
            open_trades_in_db = Trade.query.filter_by(user_id=user.id, status='open').all()
            
            for trade in open_trades_in_db:
                trade_key = (trade.symbol, trade.side)
                if trade_key not in current_open_positions:
                    # Esta posição foi fechada, buscar no histórico de ordens preenchidas
                    try:
                        print(f"[SyncService] Trade {trade.symbol} ({trade.side}) não encontrado em posições abertas. Verificando histórico de posições.")
                        # Tentar buscar posições dos últimos 7 dias para garantir que pegamos a ordem de fechamento
                        # A API da Bitget usa timestamps em milissegundos
                        end_time_ms = int(datetime.utcnow().timestamp() * 1000)
                        start_time_ms = int((datetime.utcnow() - timedelta(days=7)).timestamp() * 1000)

                        # CORREÇÃO: Usar endpoint específico de histórico de posições em vez de fills
                        print(f"[SyncService] Buscando histórico de posições para {trade.symbol}")
                        position_history = bitget_client.get_position_history(
                            symbol=trade.symbol,
                            limit=50,
                            start_time=start_time_ms,
                            end_time=end_time_ms
                        )
                        
                        if position_history and position_history.get('code') == '00000':
                            positions = position_history.get('data', {}).get('list', [])
                            print(f"[SyncService] Histórico de posições para {trade.symbol}: {len(positions)} posições encontradas.")
                            
                            found_closed_position = False
                            for position in positions:
                                # Verificar se a posição corresponde ao trade
                                pos_symbol = position.get('symbol')
                                pos_side = 'long' if position.get('holdSide') == 'long' else 'short'
                                
                                # Verificar se é a posição correta e está fechada
                                if pos_symbol == trade.symbol and pos_side == trade.side:
                                    # Verificar se a posição está fechada (size = 0 ou status closed)
                                    pos_size = float(position.get('total', 0))
                                    if pos_size == 0:  # Posição fechada
                                        exit_price = float(position.get('closeAvgPrice', 0))
                                        realized_pnl = float(position.get('achievedProfits', 0))
                                        fees = abs(float(position.get('fees', 0)))
                                        
                                        # Timestamp de fechamento
                                        closed_time = position.get('cTime')
                                        
                                        if exit_price > 0:
                                            trade.close_trade(exit_price, fees)
                                            trade.pnl = realized_pnl  # Usar PnL realizado da API
                                            
                                            if closed_time:
                                                trade.closed_at = datetime.utcfromtimestamp(int(closed_time) / 1000)
                                            
                                            closed_trades += 1
                                            found_closed_position = True
                                            print(f"[SyncService] Trade {trade.symbol} ({trade.side}) fechado via histórico de posições. Preço: {exit_price}, Fees: {fees}, PnL: {realized_pnl}")
                                            break
                            
                            if not found_closed_position:
                                print(f"[SyncService] Posição de fechamento para {trade.symbol} não encontrada no histórico recente.")
                                
                        else:
                             print(f"Erro ao buscar histórico de posições para {trade.symbol}: {position_history.get('msg')}")

                    except Exception as e:
                        print(f"Erro detalhado ao processar trade fechado {trade.id}: {e}")
                        logging.error(f"Erro ao processar trade fechado {trade.id}: {e}", exc_info=True)
            
            # 2. Obter histórico de ordens fechadas para obter o PNL correto
            # [CORREÇÃO] Trocado get_position_history por get_order_history
            closed_orders_history = bitget_client.get_order_history(limit=50) # Últimas 50 ordens

            # [DEBUG] Log temporário para inspecionar a resposta da API
            print("================= DEBUG: HISTÓRICO DE ORDENS =================")
            print(json.dumps(closed_orders_history, indent=2))
            print("==============================================================")
            
            if not closed_orders_history or 'data' not in closed_orders_history or not closed_orders_history['data'].get('orderList'):
                print(f"⚠️ Não foi possível obter histórico de ordens para o usuário {user.id}. Resposta: {closed_orders_history}")
                closed_orders_history = {'data': {'orderList': []}} # Prevenir erro
            
            # Informar sobre a sincronização bem-sucedida
            if new_trades > 0 or updated_trades > 0 or closed_trades > 0:
                print(f"Usuário {user.id}: {new_trades} novos trades, {updated_trades} trades atualizados, {closed_trades} trades fechados")

            # ** CORREÇÃO FINAL: Salvar todas as alterações no banco de dados **
            db.session.commit()

        except Exception as e:
            # Em caso de erro, reverter quaisquer alterações pendentes para não corromper o banco
            db.session.rollback()
            print(f"Erro crítico ao sincronizar trades do usuário {user.id}: {e}")
            logging.error(f"Erro crítico ao sincronizar trades do usuário {user.id}: {e}", exc_info=True)
        finally:
            # Sempre remover o usuário dos syncs ativos no final
            active_syncs.discard(user.id)

# Instância global do serviço
auto_sync_service = AutoSyncService(sync_interval=60)  # 1 minuto

def start_auto_sync(app=None):
    """Função para iniciar o serviço de sincronização automática"""
    global auto_sync_service
    if app:
        auto_sync_service = AutoSyncService(app)
    auto_sync_service.start()

def stop_auto_sync():
    """Função para parar o serviço de sincronização automática"""
    auto_sync_service.stop()

def is_auto_sync_running():
    """Verifica se o serviço de sincronização está rodando"""
    return auto_sync_service.running

def get_sync_status():
    """Retorna informações detalhadas sobre o status da sincronização"""
    return {
        'is_running': auto_sync_service.running,
        'sync_interval': auto_sync_service.sync_interval,
        'status': 'Ativo' if auto_sync_service.running else 'Inativo'
    }

def sync_nautilus_status_for_all_users():
    """
    Sincroniza o status Nautilus de todos os usuários
    Esta função é executada periodicamente para manter o status atualizado
    """
    try:
        from services.nautilus_service import nautilus_service
        
        # Buscar todos os usuários ativos
        users = User.query.filter_by(is_active=True).all()
        
        updated_users = 0
        for user in users:
            try:
                # Verificar se o usuário tem credenciais de API configuradas
                if (user.bitget_api_key_encrypted and 
                    user.bitget_api_secret_encrypted and 
                    user.bitget_passphrase_encrypted):
                    
                    # Assumir que usuários com credenciais API estão ativos no Nautilus
                    if not user.nautilus_active:
                        user.nautilus_active = True
                        updated_users += 1
                        print(f"[NautilusSync] Status do usuário {user.email} atualizado para ativo")
                        
                    # Se não tem credenciais Nautilus mas tem API, obter credenciais
                    if not user.nautilus_token or not user.nautilus_user_id:
                        try:
                            creds_result = nautilus_service.get_nautilus_credentials()
                            if creds_result['success']:
                                user.nautilus_token = creds_result['token']
                                user.nautilus_user_id = creds_result['nautilus_user_id']
                                print(f"[NautilusSync] Credenciais Nautilus obtidas para {user.email}")
                        except Exception as e:
                            print(f"[NautilusSync] Erro ao obter credenciais para {user.email}: {e}")
                            
            except Exception as e:
                print(f"[NautilusSync] Erro ao processar usuário {user.id}: {e}")
                
        if updated_users > 0:
            db.session.commit()
            print(f"[NautilusSync] {updated_users} usuários tiveram status atualizado")
        else:
            print(f"[NautilusSync] Todos os usuários já estão com status correto")
            
    except Exception as e:
        print(f"[NautilusSync] Erro geral na sincronização: {e}")
        db.session.rollback()

def sync_nautilus_status_for_user(user_id):
    """
    Sincroniza o status Nautilus de um usuário específico
    """
    try:
        from services.nautilus_service import nautilus_service
        
        user = User.query.get(user_id)
        if not user:
            return False
            
        # Se o usuário tem credenciais API, deve estar ativo no Nautilus
        if (user.bitget_api_key_encrypted and 
            user.bitget_api_secret_encrypted and 
            user.bitget_passphrase_encrypted):
            
            if not user.nautilus_active:
                user.nautilus_active = True
                db.session.commit()
                print(f"[NautilusSync] Status do usuário {user.email} corrigido para ativo")
                return True
                
        return False
        
    except Exception as e:
        print(f"[NautilusSync] Erro ao sincronizar usuário {user_id}: {e}")
        db.session.rollback()
        return False

def is_sync_running_for_user(user_id):
    """Verifica se a sincronização automática está ativa para um usuário específico"""
    global sync_active
    return sync_active and user_id in active_syncs