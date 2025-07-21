# backend/models/active_signal.py
from database import db
import json
from datetime import datetime

class ActiveSignal(db.Model):
    __tablename__ = 'active_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    symbol = db.Column(db.String(50), nullable=False)
    side = db.Column(db.String(10), nullable=False)  # 'long' ou 'short'
    entry_price = db.Column(db.Float, nullable=False)
    targets_json = db.Column(db.Text, nullable=True)  # JSON array de alvos
    targets_hit = db.Column(db.Integer, default=0)  # Número de alvos atingidos
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'
    strategy = db.Column(db.String(50), nullable=True)
    stop_loss = db.Column(db.Float, nullable=True)  # Campo adicionado
    take_profit = db.Column(db.Float, nullable=True)  # Campo adicionado
    position_size = db.Column(db.Float, nullable=True)  # Campo adicionado
    leverage = db.Column(db.Integer, nullable=True)  # Campo adicionado
    margin_mode = db.Column(db.String(20), nullable=True)  # Campo adicionado
    unrealized_pnl = db.Column(db.Float, nullable=True)  # Campo adicionado
    mark_price = db.Column(db.Float, nullable=True)  # Campo adicionado
    liquidation_price = db.Column(db.Float, nullable=True)  # Campo adicionado
    margin_ratio = db.Column(db.Float, nullable=True)  # Campo adicionado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário sem campos de datetime problemáticos"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'targets': self.targets_json,
            'targets_hit': self.targets_hit,
            'status': self.status,
            'strategy': self.strategy,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'leverage': self.leverage,
            'margin_mode': self.margin_mode,
            'unrealized_pnl': self.unrealized_pnl,
            'mark_price': self.mark_price,
            'liquidation_price': self.liquidation_price,
            'margin_ratio': self.margin_ratio
        }
    
    def get_targets_list(self):
        """Retorna lista de alvos como números"""
        if not self.targets_json:
            return []
        try:
            targets = json.loads(self.targets_json)
            return [float(t) for t in targets]
        except:
            return []
    
    def check_targets_hit(self, current_price):
        """Verifica quantos alvos foram atingidos"""
        if not self.targets_json:
            return 0
            
        targets = self.get_targets_list()
        if not targets:
            return 0
            
        hit_count = 0
        
        for target in targets:
            if self.side.lower() == 'long':
                # Para LONG: alvo atingido quando preço >= alvo
                if current_price >= target:
                    hit_count += 1
            else:
                # Para SHORT: alvo atingido quando preço <= alvo
                if current_price <= target:
                    hit_count += 1
                    
        return hit_count
    
    def update_targets_hit(self, current_price):
        """Atualiza o número de alvos atingidos"""
        self.targets_hit = self.check_targets_hit(current_price)
        return self.targets_hit