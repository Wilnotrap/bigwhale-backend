#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para replicar sinais ativos na conta demo
"""

import logging
from datetime import datetime
from models.active_signal import ActiveSignal
from models.user import User
from services.demo_bitget_api import get_demo_api
from database import db
import json

# Configurar logging
logger = logging.getLogger(__name__)

class DemoSignalReplicator:
    """Replica sinais ativos na conta demo"""
    
    def __init__(self):
        self.demo_user_email = 'financeiro@lexxusadm.com.br'
    
    def get_demo_user(self):
        """Retorna o usuário demo"""
        return User.query.filter_by(email=self.demo_user_email).first()
    
    def replicate_signal(self, signal: ActiveSignal):
        """Replica um sinal específico na conta demo"""
        try:
            demo_user = self.get_demo_user()
            if not demo_user:
                logger.error("Usuário demo não encontrado")
                return False
            
            # Obter API demo
            demo_api = get_demo_api(demo_user.id)
            
            # Preparar dados do sinal
            signal_data = {
                'symbol': signal.symbol,
                'side': signal.side,
                'leverage': 10,  # Leverage padrão para demo
                'signal_id': signal.id
            }
            
            # Executar sinal
            result = demo_api.simulate_signal_execution(signal_data)
            
            if result['success']:
                logger.info(f"Sinal {signal.id} ({signal.symbol}) replicado com sucesso na conta demo")
                return True
            else:
                logger.error(f"Erro ao replicar sinal {signal.id}: {result.get('message', 'Erro desconhecido')}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao replicar sinal {signal.id}: {str(e)}")
            return False
    
    def replicate_all_active_signals(self):
        """Replica todos os sinais ativos na conta demo"""
        try:
            # Buscar sinais ativos
            active_signals = ActiveSignal.query.filter_by(status='active').all()
            
            if not active_signals:
                logger.info("Nenhum sinal ativo encontrado para replicar")
                return True
            
            demo_user = self.get_demo_user()
            if not demo_user:
                logger.error("Usuário demo não encontrado")
                return False
            
            success_count = 0
            total_signals = len(active_signals)
            
            for signal in active_signals:
                if self.replicate_signal(signal):
                    success_count += 1
            
            logger.info(f"Replicação concluída: {success_count}/{total_signals} sinais replicados com sucesso")
            return success_count == total_signals
            
        except Exception as e:
            logger.error(f"Erro ao replicar sinais ativos: {str(e)}")
            return False
    
    def monitor_new_signals(self):
        """Monitora novos sinais e os replica automaticamente"""
        try:
            # Esta função seria chamada periodicamente ou por webhook
            # Por enquanto, vamos implementar uma verificação simples
            
            # Buscar sinais criados nos últimos 5 minutos que ainda não foram replicados
            from datetime import timedelta
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            
            new_signals = ActiveSignal.query.filter(
                ActiveSignal.created_at >= recent_time,
                ActiveSignal.status == 'active'
            ).all()
            
            if new_signals:
                logger.info(f"Encontrados {len(new_signals)} novos sinais para replicar")
                
                for signal in new_signals:
                    self.replicate_signal(signal)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao monitorar novos sinais: {str(e)}")
            return False
    
    def get_demo_performance(self):
        """Retorna performance da conta demo"""
        try:
            demo_user = self.get_demo_user()
            if not demo_user:
                return None
            
            demo_api = get_demo_api(demo_user.id)
            
            # Obter estatísticas
            stats = demo_api.get_trading_stats()
            balance = demo_api.get_account_balance()
            positions = demo_api.get_positions()
            
            return {
                'stats': stats.get('stats', {}),
                'balance': balance.get('balance', {}),
                'open_positions': len(positions.get('positions', [])),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter performance demo: {str(e)}")
            return None

# Instância global do replicador
demo_replicator = DemoSignalReplicator()

def replicate_signal_to_demo(signal_id: int):
    """Função helper para replicar um sinal específico"""
    try:
        signal = ActiveSignal.query.get(signal_id)
        if signal:
            return demo_replicator.replicate_signal(signal)
        return False
    except Exception as e:
        logger.error(f"Erro ao replicar sinal {signal_id}: {str(e)}")
        return False

def get_demo_performance():
    """Função helper para obter performance da demo"""
    return demo_replicator.get_demo_performance()