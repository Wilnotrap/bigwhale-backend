import logging
from typing import Dict

logger = logging.getLogger(__name__)

class DemoBitgetAPI:
    def __init__(self, user_id: int, initial_balance: float = 600.0):
        self.user_id = user_id
        self.balance = initial_balance
        self.positions = {}
        self.trades_history = []
        
        logger.info(f"Inicializando API demo para usuário {user_id} com saldo ${initial_balance}")
        
        self.current_prices = {
            'BTCUSDT': 45000.0,
            'ETHUSDT': 3200.0,
            'ADAUSDT': 0.45,
            'SOLUSDT': 95.0,
        }
    
    def get_account_balance(self) -> Dict:
        return {
            'success': True,
            'balance': {
                'total_balance': self.balance,
                'available_balance': self.balance,
                'margin_balance': 0.0,
                'unrealized_pnl': 0.0,
                'currency': 'USDT'
            }
        }
    
    def get_positions(self) -> Dict:
        return {
            'success': True,
            'positions': []
        }
    
    def get_trading_stats(self) -> Dict:
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

demo_api_instance = None

def get_demo_api(user_id: int) -> DemoBitgetAPI:
    global demo_api_instance
    
    if demo_api_instance is None or demo_api_instance.user_id != user_id:
        demo_api_instance = DemoBitgetAPI(user_id)
    
    return demo_api_instance