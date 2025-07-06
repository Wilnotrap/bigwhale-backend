# backend/models/trade.py
from datetime import datetime
from sqlalchemy import func, desc, case, cast, Float, text, event, DDL
from sqlalchemy.orm import relationship
from database import db
from api.bitget_client import BitgetAPI
from utils.security import decrypt_api_key
from utils.currency import get_brl_to_usd_rate
import logging

logger = logging.getLogger(__name__)

class Trade(db.Model):
    """Modelo para armazenar informações de trades"""
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informações básicas do trade
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False)
    size = db.Column(db.String(50))
    
    # Preços
    entry_price = db.Column(db.String(50))
    exit_price = db.Column(db.String(50))
    
    # Detalhes do trade
    leverage = db.Column(db.Float)
    status = db.Column(db.String(20), default='open')
    
    # Timestamps
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # Resultados
    pnl = db.Column(db.Float)
    roe = db.Column(db.Float)
    fees = db.Column(db.Float, default=0.0)
    
    # NOVA COLUNA: Margem usada na operação
    margin = db.Column(db.Float)
    
    # IDs de referência
    bitget_order_id = db.Column(db.String(100), unique=True, nullable=True)
    bitget_position_id = db.Column(db.String(100), nullable=True)
    
    # Relacionamento
    user = relationship('User', back_populates='trades')
    
    @staticmethod
    def get_user_stats(user_id):
        logger.info(f"[DEBUG] Iniciando get_user_stats para usuário {user_id}")
        
        from models.user import User
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}
            
        realized_pnl = 0
        unrealized_pnl = 0
        total_trades = 0
        winning_trades = 0
        account_balance_usd = 0
        open_positions_count = 0
        api_status = {'valid': False, 'error_message': 'Credenciais não configuradas.'}

        try:
            # Verificar se todas as credenciais existem
            if not all([user.bitget_api_key_encrypted, user.bitget_api_secret_encrypted, user.bitget_passphrase_encrypted]):
                api_status = {'valid': False, 'error_message': 'Credenciais da API não configuradas.'}
                logger.warning(f"Credenciais da API não configuradas para usuário {user_id}")
            else:
                # Descriptografar credenciais
                api_key_decrypted = decrypt_api_key(user.bitget_api_key_encrypted)
                api_secret_decrypted = decrypt_api_key(user.bitget_api_secret_encrypted)
                passphrase_decrypted = decrypt_api_key(user.bitget_passphrase_encrypted)
            
                if not all([api_key_decrypted, api_secret_decrypted, passphrase_decrypted]):
                    api_status = {'valid': False, 'error_message': 'Erro ao descriptografar credenciais.'}
                    logger.error(f"Erro ao descriptografar credenciais para usuário {user_id}")
                else:
                    # Criar cliente Bitget e validar credenciais
                    bitget_client = BitgetAPI(api_key_decrypted, api_secret_decrypted, passphrase_decrypted)
                
                    # Validar credenciais
                    if not bitget_client.validate_credentials():
                        api_status = {'valid': False, 'error_message': 'Credenciais da API inválidas.'}
                        logger.error(f"Credenciais da API inválidas para usuário {user_id}")
                    else:
                        # Buscar saldo e posições
                        logger.info("Buscando saldo da conta de futuros na Bitget...")
                        balance_response = bitget_client.get_futures_balance()
                
                        if balance_response and balance_response.get('code') == '00000':
                            api_status = {'valid': True, 'error_message': None}
                            for account in balance_response.get('data', []):
                                if account.get('marginCoin') == 'USDT':
                                    account_balance_usd = float(account.get('accountEquity', 0))
                                    logger.info(f"Saldo em USDT encontrado: {account_balance_usd}")
                                    break
                        else:
                            error_msg = balance_response.get('msg', 'Erro desconhecido ao buscar saldo.') if balance_response else 'Sem resposta da API'
                            api_status = {'valid': False, 'error_message': error_msg}
                            logger.error(f"Erro ao buscar saldo da Bitget para usuário {user_id}: {error_msg}")

                        # Buscar posições abertas
                        positions_response = bitget_client.get_futures_positions()
                        if positions_response and positions_response.get('code') == '00000':
                            open_positions = positions_response.get('data', [])
                            open_positions_count = len(open_positions)
                            for pos in open_positions:
                                pnl_value = float(pos.get('unrealizedPL', 0))
                                unrealized_pnl += pnl_value
                        else:
                            error_msg = positions_response.get('msg', 'Erro desconhecido na API') if positions_response else 'Nenhuma resposta da API'
                            api_status = {'valid': False, 'error_message': error_msg}
                            logger.error(f"Erro ao buscar posições abertas da Bitget para user {user_id}: {error_msg}")

        except Exception as e:
            logger.error(f"Erro de exceção ao buscar dados da Bitget para user {user_id}: {e}")
            api_status = {'valid': False, 'error_message': str(e)}

        # Buscar estatísticas do banco de dados
        try:
            realized_pnl_query = db.session.query(func.sum(Trade.pnl)).filter(
                Trade.user_id == user_id, 
                Trade.status == 'closed'
            ).scalar()
            realized_pnl = realized_pnl_query or 0

            total_trades_query = db.session.query(func.count(Trade.id)).filter(
                Trade.user_id == user_id, 
                Trade.status == 'closed'
            ).scalar()
            total_trades = total_trades_query or 0

            winning_trades_query = db.session.query(func.count(Trade.id)).filter(
                Trade.user_id == user_id, 
                Trade.status == 'closed', 
                Trade.pnl > 0
            ).scalar()
            winning_trades = winning_trades_query or 0
            
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            total_pnl = realized_pnl + unrealized_pnl
            
            stats = {
                'realized_pnl': realized_pnl,
                'unrealized_pnl': unrealized_pnl,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'total_trades': total_trades,
                'open_positions_count': open_positions_count,
                'winning_trades': winning_trades,
                'account_balance_usd': account_balance_usd,
                'operational_balance': user.operational_balance or 0,
                'operational_balance_usd': user.operational_balance_usd or 0,
                'operational_balance_percentage': user.get_operational_balance_percentage(),
                'remaining_balance_usd': user.get_remaining_balance_usd(),
                'api_status': api_status
            }
            
            logger.info(f"[DEBUG] Stats obtidas com sucesso: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas do banco de dados para usuário {user_id}: {e}")
            return {
                'error': 'Erro ao buscar estatísticas',
                'api_status': api_status
            }

    def to_dict(self):
        """Converte o objeto Trade para um dicionário serializável."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'leverage': self.leverage,
            'status': self.status,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'pnl': self.pnl,
            'roe': self.roe,
            'fees': self.fees,
            'margin': self.margin,
            'bitget_order_id': self.bitget_order_id,
            'bitget_position_id': self.bitget_position_id,
        }

    def calculate_roe(self):
        """Calcula o ROE baseado no PnL e na margem real investida."""
        if not self.pnl or not self.margin:
            return 0.0
            
        try:
            pnl = float(self.pnl)
            margin = float(self.margin)
            
            if margin == 0:
                return 0.0
                
            # ROE = (PnL / Margem Real Investida) * 100
            roe = (pnl / margin) * 100
            
            return roe
        except (ValueError, TypeError):
            return 0.0
    
    def calculate_current_roe(self, bitget_client):
        """Calcula o ROE atual baseado no preço de mercado em tempo real."""
        if not self.entry_price or not self.margin or not self.size:
            return 0.0
            
        try:
            # Obter preço atual de mercado
            ticker_response = bitget_client.get_ticker(self.symbol)
            if not ticker_response or ticker_response.get('code') != '00000':
                # Fallback para ROE armazenado se não conseguir obter preço atual
                return self.roe or 0.0
                
            current_price = float(ticker_response.get('data', {}).get('lastPr', 0))
            if current_price <= 0:
                return self.roe or 0.0
                
            entry_price = float(self.entry_price)
            size = float(self.size)
            margin = float(self.margin)
            
            if margin <= 0 or entry_price <= 0:
                return 0.0
                
            # Calcular PnL não realizado
            if self.side.lower() == 'long':
                # Para posições long: PnL = (preço_atual - preço_entrada) * tamanho
                unrealized_pnl = (current_price - entry_price) * size
            else:
                # Para posições short: PnL = (preço_entrada - preço_atual) * tamanho
                unrealized_pnl = (entry_price - current_price) * size
                
            # Calcular ROE: (PnL não realizado / margem real) * 100
            current_roe = (unrealized_pnl / margin) * 100
            
            return current_roe
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Erro ao calcular ROE atual para trade {self.id}: {e}")
            # Fallback para ROE armazenado
            return self.roe or 0.0

    def close_trade(self, exit_price, fees=0.0):
        """Fecha um trade definindo o preço de saída, fees e status"""
        self.exit_price = exit_price
        self.fees = fees
        self.status = 'closed'
        self.closed_at = datetime.utcnow()
        
        # Calcular ROE automaticamente
        self.roe = self.calculate_roe()
        
        # Descontar comissão automaticamente se PnL for positivo
        self._deduct_commission_on_close()
    
    def _deduct_commission_on_close(self):
        """Deduz comissão do saldo do usuário quando trade fecha com PnL positivo"""
        if self.pnl <= 0:
            return
        
        from .user import User
        from database import db
        
        user = User.query.get(self.user_id)
        if not user:
            return
        
        # Calcular comissão (35% do PnL positivo)
        commission = self.pnl * 0.35
        
        # Deduzir primeiro do saldo USD
        user.operational_balance_usd -= commission
        
        # Se ficou negativo em USD, converter o valor negativo para BRL
        if user.operational_balance_usd < 0:
            negative_amount_usd = abs(user.operational_balance_usd)
            user.operational_balance_usd = 0
            
            # Converter para BRL usando taxa de câmbio atual
            try:
                brl_to_usd_rate = get_brl_to_usd_rate()
                usd_to_brl_rate = 1 / brl_to_usd_rate if brl_to_usd_rate > 0 else 5.0
                negative_amount_brl = negative_amount_usd * usd_to_brl_rate
            except:
                # Fallback para taxa fixa se houver erro
                negative_amount_brl = negative_amount_usd * 5.0
            
            user.operational_balance -= negative_amount_brl
        
        # Salvar alterações
        db.session.commit()

    def __repr__(self):
        return f'<Trade {self.id}>'