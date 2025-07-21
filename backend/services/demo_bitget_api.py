#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Simulada da Bitget para Conta Demo
Simula operações reais para gerar métricas e histórico
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class DemoBitgetAPI:
    """API simulada da Bitget para conta demo"""
    
    def __init__(self, user_id: int, initial_balance: float = 600.0):
        self.user_id = user_id
        self.balance = initial_balance
        self.positions = {}  # symbol -> position_data
        self.orders = {}     # order_id -> order_data
        self.trades_history = []
        self.order_counter = 1000
        
        # Preços simulados (atualizados dinamicamente)
        self.current_prices = {
            'BTCUSDT': 45000.0,
            'ETHUSDT': 3200.0,
            'ADAUSDT': 0.45,
            'SOLUSDT': 95.0,
            'DOTUSDT': 7.2,
            'LINKUSDT': 15.8,
            'AVAXUSDT': 38.5,
            'MATICUSDT': 0.85,
            'ATOMUSDT': 12.4,
            'NEARUSDT': 4.2
        }
        
        # Volatilidade por símbolo (para simulação realista)
        self.volatility = {
            'BTCUSDT': 0.02,    # 2% de volatilidade
            'ETHUSDT': 0.025,   # 2.5%
            'ADAUSDT': 0.03,    # 3%
            'SOLUSDT': 0.035,   # 3.5%
            'DOTUSDT': 0.03,
            'LINKUSDT': 0.028,
            'AVAXUSDT': 0.04,
            'MATICUSDT': 0.035,
            'ATOMUSDT': 0.032,
            'NEARUSDT': 0.038
        }
    
    def update_prices(self):
        """Atualiza preços com movimento realista"""
        for symbol in self.current_prices:
            current_price = self.current_prices[symbol]
            volatility = self.volatility.get(symbol, 0.02)
            
            # Movimento aleatório baseado na volatilidade
            change_percent = random.uniform(-volatility, volatility)
            new_price = current_price * (1 + change_percent)
            
            # Garantir que o preço não seja negativo
            self.current_prices[symbol] = max(new_price, current_price * 0.5)
    
    def get_account_balance(self) -> Dict:
        """Retorna saldo da conta"""
        # Calcular PnL não realizado
        unrealized_pnl = 0.0
        for position in self.positions.values():
            if position['status'] == 'open':
                current_price = self.current_prices.get(position['symbol'], position['entry_price'])
                if position['side'] == 'long':
                    pnl = (current_price - position['entry_price']) * position['size']
                else:  # short
                    pnl = (position['entry_price'] - current_price) * position['size']
                unrealized_pnl += pnl
        
        return {
            'success': True,
            'balance': {
                'total_balance': self.balance + unrealized_pnl,
                'available_balance': self.balance,
                'margin_balance': sum(pos['margin'] for pos in self.positions.values() if pos['status'] == 'open'),
                'unrealized_pnl': unrealized_pnl,
                'currency': 'USDT'
            }
        }
    
    def get_positions(self) -> Dict:
        """Retorna posições abertas"""
        open_positions = []
        
        for position in self.positions.values():
            if position['status'] == 'open':
                current_price = self.current_prices.get(position['symbol'], position['entry_price'])
                
                if position['side'] == 'long':
                    unrealized_pnl = (current_price - position['entry_price']) * position['size']
                else:  # short
                    unrealized_pnl = (position['entry_price'] - current_price) * position['size']
                
                pnl_percentage = (unrealized_pnl / position['margin']) * 100 if position['margin'] > 0 else 0
                
                open_positions.append({
                    'symbol': position['symbol'],
                    'side': position['side'].upper(),
                    'size': position['size'],
                    'entry_price': position['entry_price'],
                    'current_price': current_price,
                    'unrealized_pnl': unrealized_pnl,
                    'pnl_percentage': pnl_percentage,
                    'leverage': position['leverage'],
                    'margin': position['margin']
                })
        
        return {
            'success': True,
            'positions': open_positions
        }
    
    def place_order(self, symbol: str, side: str, size: float, price: float = None, 
                   order_type: str = 'market', leverage: int = 1) -> Dict:
        """Simula colocação de ordem"""
        try:
            self.update_prices()
            
            # Usar preço de mercado se não especificado
            if price is None:
                price = self.current_prices.get(symbol, 45000.0)
            
            # Calcular margem necessária
            margin_required = (size * price) / leverage
            
            # Verificar se há saldo suficiente
            if margin_required > self.balance:
                return {
                    'success': False,
                    'message': 'Saldo insuficiente'
                }
            
            # Gerar ID da ordem
            order_id = f"demo_{self.order_counter}"
            self.order_counter += 1
            
            # Simular execução imediata para ordens de mercado
            if order_type == 'market':
                # Adicionar pequeno slippage
                execution_price = price * (1 + random.uniform(-0.001, 0.001))
                
                # Criar posição
                position_id = f"pos_{len(self.positions) + 1}"
                self.positions[position_id] = {
                    'id': position_id,
                    'symbol': symbol,
                    'side': side.lower(),
                    'size': size,
                    'entry_price': execution_price,
                    'leverage': leverage,
                    'margin': margin_required,
                    'status': 'open',
                    'created_at': datetime.now(),
                    'stop_loss': None,
                    'take_profit': None
                }
                
                # Reduzir saldo disponível
                self.balance -= margin_required
                
                # Registrar trade
                trade = {
                    'id': order_id,
                    'symbol': symbol,
                    'side': side,
                    'size': size,
                    'price': execution_price,
                    'leverage': leverage,
                    'margin': margin_required,
                    'timestamp': datetime.now(),
                    'status': 'filled'
                }
                self.trades_history.append(trade)
                
                return {
                    'success': True,
                    'order_id': order_id,
                    'position_id': position_id,
                    'execution_price': execution_price,
                    'message': 'Ordem executada com sucesso'
                }
            
            return {
                'success': False,
                'message': 'Tipo de ordem não suportado na demo'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao executar ordem: {str(e)}'
            }
    
    def close_position(self, position_id: str, price: float = None) -> Dict:
        """Fecha uma posição"""
        try:
            if position_id not in self.positions:
                return {
                    'success': False,
                    'message': 'Posição não encontrada'
                }
            
            position = self.positions[position_id]
            
            if position['status'] != 'open':
                return {
                    'success': False,
                    'message': 'Posição já fechada'
                }
            
            self.update_prices()
            
            # Usar preço de mercado se não especificado
            if price is None:
                price = self.current_prices.get(position['symbol'], position['entry_price'])
            
            # Calcular PnL
            if position['side'] == 'long':
                pnl = (price - position['entry_price']) * position['size']
            else:  # short
                pnl = (position['entry_price'] - price) * position['size']
            
            # Atualizar saldo
            self.balance += position['margin'] + pnl
            
            # Fechar posição
            position['status'] = 'closed'
            position['close_price'] = price
            position['pnl'] = pnl
            position['closed_at'] = datetime.now()
            
            # Registrar trade de fechamento
            trade = {
                'id': f"close_{position_id}",
                'symbol': position['symbol'],
                'side': 'sell' if position['side'] == 'long' else 'buy',
                'size': position['size'],
                'price': price,
                'pnl': pnl,
                'timestamp': datetime.now(),
                'status': 'filled'
            }
            self.trades_history.append(trade)
            
            return {
                'success': True,
                'pnl': pnl,
                'close_price': price,
                'message': 'Posição fechada com sucesso'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao fechar posição: {str(e)}'
            }
    
    def get_trading_stats(self) -> Dict:
        """Retorna estatísticas de trading"""
        try:
            closed_positions = [pos for pos in self.positions.values() if pos['status'] == 'closed']
            
            if not closed_positions:
                return {
                    'success': True,
                    'stats': {
                        'total_trades': 0,
                        'winning_trades': 0,
                        'losing_trades': 0,
                        'win_rate': 0.0,
                        'total_profit': 0.0,
                        'total_loss': 0.0,
                        'net_profit': 0.0,
                        'average_profit': 0.0,
                        'average_loss': 0.0,
                        'profit_factor': 0.0
                    }
                }
            
            total_trades = len(closed_positions)
            winning_trades = len([pos for pos in closed_positions if pos.get('pnl', 0) > 0])
            losing_trades = total_trades - winning_trades
            
            profits = [pos['pnl'] for pos in closed_positions if pos.get('pnl', 0) > 0]
            losses = [pos['pnl'] for pos in closed_positions if pos.get('pnl', 0) < 0]
            
            total_profit = sum(profits) if profits else 0.0
            total_loss = sum(losses) if losses else 0.0
            net_profit = total_profit + total_loss
            
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
            average_profit = total_profit / len(profits) if profits else 0.0
            average_loss = total_loss / len(losses) if losses else 0.0
            profit_factor = abs(total_profit / total_loss) if total_loss != 0 else 0.0
            
            return {
                'success': True,
                'stats': {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'total_profit': total_profit,
                    'total_loss': total_loss,
                    'net_profit': net_profit,
                    'average_profit': average_profit,
                    'average_loss': average_loss,
                    'profit_factor': profit_factor
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao calcular estatísticas: {str(e)}'
            }
    
    def simulate_signal_execution(self, signal_data: Dict) -> Dict:
        """Simula execução de um sinal do Nautilus"""
        try:
            symbol = signal_data.get('symbol', 'BTCUSDT')
            side = signal_data.get('side', 'long')
            
            # Calcular tamanho da posição (2% do saldo)
            position_size_usd = self.balance * 0.02
            current_price = self.current_prices.get(symbol, 45000.0)
            size = position_size_usd / current_price
            
            # Executar ordem
            result = self.place_order(
                symbol=symbol,
                side=side,
                size=size,
                leverage=signal_data.get('leverage', 10)
            )
            
            if result['success']:
                # Simular fechamento automático após algum tempo (para demo)
                # Em produção, isso seria baseado nos alvos do sinal
                return {
                    'success': True,
                    'message': 'Sinal executado com sucesso',
                    'position_id': result['position_id'],
                    'execution_price': result['execution_price']
                }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao executar sinal: {str(e)}'
            }

# Instância global para a conta demo
demo_api_instance = None

def get_demo_api(user_id: int) -> DemoBitgetAPI:
    """Retorna instância da API demo para o usuário"""
    global demo_api_instance
    
    if demo_api_instance is None or demo_api_instance.user_id != user_id:
        demo_api_instance = DemoBitgetAPI(user_id)
    
    return demo_api_instance