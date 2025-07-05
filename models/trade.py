# backend/models/trade.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import relationship
from database import db
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
    margin = db.Column(db.Float)
    
    # IDs de referência
    bitget_order_id = db.Column(db.String(100), unique=True, nullable=True)
    bitget_position_id = db.Column(db.String(100), nullable=True)
    
    # Relacionamento
    user = relationship('User', back_populates='trades')
    
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
    
    def __repr__(self):
        return f'<Trade {self.id}>'