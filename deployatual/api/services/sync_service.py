import threading
import time
import logging
from datetime import datetime, timedelta
from models import User, Trade, db
from bitget_client import BitgetClient
from utils.encryption import decrypt_api_credentials
import json

# Variáveis globais para controle da sincronização
sync_active = False
active_syncs = set()  # Set para rastrear usuários em sincronização ativa

class AutoSyncService:
    def __init__(self, app=None, sync_interval=60):
        self.app = app
        self.sync_interval = sync_interval  # Intervalo em segundos
        self.running = False
        self.thread = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o serviço com o app Flask"""
        self.app = app
        
    def start(self):
        """Inicia o serviço de sincronização automática"""
        global sync_active
        if not self.running:
            self.running = True
            sync_active = True
            self.thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.thread.start()
            print(f"[AutoSyncService] Serviço iniciado com intervalo de {self.sync_interval} segundos")
    
    def stop(self):
        """Para o serviço de sincronização automática"""
        global sync_active
        self.running = False
        sync_active = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[AutoSyncService] Serviço parado")
    
    def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.running:
            try:
                if self.app:
                    with self.app.app_context():
                        self.sync_all_users()
                else:
                    self.sync_all_users()
                    
                # Aguardar o intervalo antes da próxima sincronização
                time.sleep(self.sync_interval)
                
            except Exception as e:
                print(f"[AutoSyncService] Erro no loop de sincronização: {e}")
                logging.error(f"Erro no loop de sincronização: {e}", exc_info=True)
                time.sleep(30)  # Aguardar 30 segundos antes de tentar novamente
    
    def sync_all_users(self):
        """Sincroniza trades de todos os usuários ativos"""
        try:
            # Buscar usuários ativos com credenciais configuradas
            users = User.query.filter(
                User.is_active == True,
                User.bitget_api_key_encrypted.isnot(None),
                User.bitget_api_secret_encrypted.isnot(None),
                User.bitget_passphrase_encrypted.isnot(None)
            ).all()
            
            print(f"[AutoSyncService] Sincronizando {len(users)} usuários ativos")
            
            for user in users:
                try:
                    # Verificar se o usuário já está em sincronização
                    if user.id in active_syncs:
                        print(f"[AutoSyncService] Usuário {user.id} já está em sincronização, pulando...")
                        continue
                        
                    self.sync_user_trades(user)
                    
                except Exception as e:
                    print(f"[AutoSyncService] Erro ao sincronizar usuário {user.id}: {e}")
                    logging.error(f"Erro ao sincronizar usuário {user.id}: {e}", exc_info=True)
                    # Remover usuário dos syncs ativos em caso de erro
                    active_syncs.discard(user.id)
            
            # Sincronizar status Nautilus periodicamente (a cada 10 ciclos)
            if hasattr(self, '_sync_counter'):
                self._sync_counter += 1
            else:
                self._sync_counter = 1
                
            if self._sync_counter % 10 == 0:
                print("[AutoSyncService] Sincronizando status Nautilus de todos os usuários")
                sync_nautilus_status_for_all_users()
                
        except Exception as e:
            print(f"[AutoSyncService] Erro geral na sincronização: {e}")
            logging.error(f"Erro geral na sincronização: {e}", exc_info=True)
    
    def sync_user_trades(self, user):
        """Sincroniza trades de um usuário específico"""
        global active_syncs
        
        # Adicionar usuário aos syncs ativos
        active_syncs.add(user.id)
        
        try:
            print(f"[SyncService] Iniciando sincronização para usuário {user.id}")
            
            # Descriptografar credenciais
            try:
                api_key, api_secret, passphrase = decrypt_api_credentials(
                    user.bitget_api_key_encrypted,
                    user.bitget_api_secret_encrypted,
                    user.bitget_passphrase_encrypted
                )
            except Exception as e:
                print(f"Erro ao descriptografar credenciais do usuário {user.id}: {e}")
                return
            
            # Criar cliente Bitget
            bitget_client = BitgetClient(api_key, api_secret, passphrase)
            
            # 1. Obter saldo de futuros
            balance_response = bitget_client.get_futures_balance()
            if not balance_response or balance_response.get('code') != '00000':
                print(f"Erro ao obter saldo de futuros para usuário {user.id}: {balance_response}")
                return
            
            # 2. Obter posições abertas
            positions_response = bitget_client.get_open_positions()
            if not positions_response or positions_response.get('code') != '00000':
                print(f"Erro ao obter posições abertas para usuário {user.id}: {positions_response}")
                return
            
            positions = positions_response.get('data', [])
            print(f"[SyncService] Usuário {user.id}: {len(positions)} posições abertas encontradas")
            
            # Mapear posições atuais
            current_open_positions = {}
            for position in positions:
                symbol = position.get('symbol')
                side = 'long' if position.get('holdSide') == 'long' else 'short'
                size = float(position.get('total', 0))
                
                if size > 0:  # Apenas posições com tamanho > 0
                    current_open_positions[(symbol, side)] = {
                        'size': size,
                        'entry_price': float(position.get('averageOpenPrice', 0)),
                        'unrealized_pnl': float(position.get('unrealizedPL', 0)),
                        'leverage': float(position.get('leverage', 1))
                    }
            
            # Contadores para relatório
            new_trades = 0
            updated_trades = 0
            closed_trades = 0
            
            # Verificar trades existentes e atualizar
            for (symbol, side), position_data in current_open_positions.items():
                size = position_data['size']
                entry_price = position_data['entry_price']
                unrealized_pnl = position_data['unrealized_pnl']
                leverage = position_data['leverage']
                
                # Buscar trade existente
                existing_trade = Trade.query.filter_by(
                    user_id=user.id,
                    symbol=symbol,
                    side=side,
                    status='open'
                ).first()
                
                if existing_trade:
                    # Atualizar trade existente
                    existing_trade.size = size
                    existing_trade.pnl = unrealized_pnl
                    existing_trade.leverage = leverage
                    
                    # Atualizar preço de entrada se mudou significativamente (pode indicar aporte)
                    if abs(existing_trade.entry_price - entry_price) > 0.01:
                        print(f"[SyncService] Preço de entrada atualizado para {symbol} ({side}): {existing_trade.entry_price} -> {entry_price}")
                        existing_trade.entry_price = entry_price
                    
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