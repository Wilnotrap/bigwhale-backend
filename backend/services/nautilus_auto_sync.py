#!/usr/bin/env python3
"""
Serviço de Sincronização Automática com Nautilus
Busca sinais ativos automaticamente e salva no banco
"""

import threading
import time
import logging
import requests
from datetime import datetime, timedelta
from models.active_signal import ActiveSignal
from database import db
from services.nautilus_service import nautilus_service

class NautilusAutoSync:
    """
    Serviço que sincroniza automaticamente sinais do Nautilus
    """
    
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        self.last_sync = None
        self.sync_interval = 300  # 5 minutos
        
    def start(self):
        """Inicia a sincronização automática"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.thread.start()
            self.logger.info("🔄 Sincronização automática com Nautilus iniciada")
    
    def stop(self):
        """Para a sincronização automática"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("🛑 Sincronização automática parada")
    
    def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.running:
            try:
                with self.app.app_context():
                    self._sync_active_signals()
                
                # Aguardar intervalo configurado
                time.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"Erro na sincronização automática: {e}")
                time.sleep(60)  # Aguardar 1 minuto em caso de erro
    
    def _sync_active_signals(self):
        """Sincroniza sinais ativos do Nautilus"""
        try:
            self.logger.info("🔄 Iniciando sincronização com Nautilus...")
            
            # Garantir autenticação com o Nautilus
            auth_result = nautilus_service.ensure_authenticated()
            if not auth_result['success']:
                self.logger.warning(f"Falha na autenticação com Nautilus: {auth_result.get('error')}")
                return
            
            # Buscar operações ativas do Nautilus
            url = f"{nautilus_service.base_url}/operation/active-operations"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'{nautilus_service.token}',
                'auth-userid': str(nautilus_service.user_id)
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                operations_data = response.json()
                self.logger.info(f"📊 {len(operations_data) if isinstance(operations_data, list) else 0} operações obtidas do Nautilus")
                
                # Processar e salvar sinais
                saved_count = self._process_and_save_signals(operations_data)
                
                if saved_count > 0:
                    self.logger.info(f"💾 {saved_count} sinais sincronizados com sucesso")
                
                self.last_sync = datetime.now()
                
            else:
                self.logger.warning(f"Erro ao buscar operações: HTTP {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Erro na sincronização: {e}")
    
    def _process_and_save_signals(self, operations_data):
        """Processa e salva sinais no banco"""
        if not isinstance(operations_data, list):
            return 0
        
        saved_count = 0
        
        for operation in operations_data:
            try:
                # Extrair dados essenciais
                symbol = operation.get('symbol', '').replace('USDT', '') + 'USDT'
                side = operation.get('side', '').lower()
                entry_price = operation.get('price') or operation.get('entry_price') or operation.get('entryPrice')
                
                # Extrair alvos
                targets = []
                
                # Formato 1: targets como lista
                if 'targets' in operation and isinstance(operation['targets'], list):
                    targets = [float(t) for t in operation['targets'] if t is not None]
                
                # Formato 2: alvos individuais (target1, target2, etc.)
                elif any(f'target{i}' in operation for i in range(1, 6)):
                    for i in range(1, 6):
                        target_key = f'target{i}'
                        if target_key in operation and operation[target_key] is not None and operation[target_key] != '':
                            targets.append(float(operation[target_key]))
                
                # Formato 3: tp1, tp2, tp3, etc.
                elif any(f'tp{i}' in operation for i in range(1, 6)):
                    for i in range(1, 6):
                        tp_key = f'tp{i}'
                        if tp_key in operation and operation[tp_key] is not None and operation[tp_key] != '':
                            targets.append(float(operation[tp_key]))
                
                # Validar dados essenciais
                if not symbol or not side or not targets or not entry_price:
                    self.logger.debug(f"Operação ignorada: symbol={bool(symbol)}, side={bool(side)}, targets={len(targets)}, entry_price={bool(entry_price)}")
                    continue
                
                # Verificar se já existe um sinal ativo para este símbolo/lado
                existing_signal = ActiveSignal.query.filter_by(
                    symbol=symbol,
                    side=side,
                    status='active'
                ).first()
                
                if existing_signal:
                    # Atualizar sinal existente
                    existing_signal.entry_price = float(entry_price)
                    existing_signal.targets = targets
                    existing_signal.stop_loss = float(operation.get('stop_loss', 0)) if operation.get('stop_loss') else None
                    existing_signal.strategy = operation.get('strategy', existing_signal.strategy)
                    existing_signal.updated_at = datetime.utcnow()
                    
                    self.logger.debug(f"🔄 Sinal atualizado: {symbol} {side.upper()}")
                    
                else:
                    # Criar novo sinal
                    new_signal = ActiveSignal(
                        user_id=1,  # Usuário admin padrão
                        symbol=symbol,
                        side=side,
                        entry_price=float(entry_price),
                        stop_loss=float(operation.get('stop_loss', 0)) if operation.get('stop_loss') else None,
                        strategy=operation.get('strategy'),
                        status='active'
                    )
                    new_signal.targets = targets
                    
                    db.session.add(new_signal)
                    self.logger.debug(f"✅ Novo sinal criado: {symbol} {side.upper()}")
                
                saved_count += 1
                
            except Exception as e:
                self.logger.error(f"Erro ao processar operação: {e}")
                continue
        
        # Salvar todas as alterações
        if saved_count > 0:
            db.session.commit()
        
        return saved_count
    
    def force_sync(self):
        """Força uma sincronização imediata"""
        try:
            with self.app.app_context():
                self.logger.info("🔄 Sincronização forçada iniciada")
                self._sync_active_signals()
                self.logger.info("✅ Sincronização forçada concluída")
                return True
        except Exception as e:
            self.logger.error(f"Erro na sincronização forçada: {e}")
            return False

# Instância global do serviço
nautilus_sync = None

def init_nautilus_sync(app):
    """Inicializa o serviço de sincronização automática"""
    global nautilus_sync
    nautilus_sync = NautilusAutoSync(app)
    nautilus_sync.start()
    return nautilus_sync

def get_nautilus_sync():
    """Retorna a instância do serviço de sincronização"""
    return nautilus_sync 