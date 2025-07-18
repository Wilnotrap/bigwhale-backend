from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.security import aes_encrypt, aes_decrypt
from sqlalchemy import event
from sqlalchemy.orm import attributes

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bitget_api_key_encrypted = db.Column(db.String(512), nullable=True)
    bitget_api_secret_encrypted = db.Column(db.String(512), nullable=True)
    bitget_passphrase_encrypted = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    nautilus_trader_id = db.Column(db.String(120), nullable=True)
    operational_balance = db.Column(db.Float, default=0.0)
    operational_balance_usd = db.Column(db.Float, default=0.0)  # Saldo operacional em USD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    commission_rate = db.Column(db.Float, default=0.5)  # Taxa de comissão de 50%
    api_configured = db.Column(db.Boolean, default=False, nullable=False)

    # Relacionamento com Trade
    trades = db.relationship('Trade', back_populates='user', lazy=True)

    def set_password(self, password):
        """Criptografa e define a senha do usuário usando Werkzeug."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta usando Werkzeug."""
        return check_password_hash(self.password_hash, password)
    
    def get_operational_balance_percentage(self):
        """
        Calcula a porcentagem do saldo operacional já utilizado
        Retorna: float - Porcentagem utilizada (0-100)
        """
        try:
            # Buscar total de comissões cobradas
            from sqlalchemy import text
            result = db.session.execute(
                text("""
                    SELECT COALESCE(SUM(t.pnl * :commission_rate), 0) as total_commissions
                    FROM trades t 
                    WHERE t.user_id = :user_id 
                    AND t.status = 'closed' 
                    AND t.pnl > 0
                """),
                {
                    'user_id': self.id,
                    'commission_rate': self.commission_rate
                }
            ).fetchone()
            
            total_commissions = float(result[0]) if result and result[0] else 0.0
            
            # Calcular saldo inicial: saldo atual + comissões já cobradas
            current_balance = getattr(self, 'operational_balance_usd', 0.0) or 0.0
            initial_balance = current_balance + total_commissions
            
            # Se não há saldo inicial, retorna 0%
            if initial_balance <= 0:
                return 0.0
            
            # Calcular porcentagem utilizada
            percentage_used = (total_commissions / initial_balance) * 100
            
            return min(percentage_used, 100.0)  # Máximo 100%
            
        except Exception as e:
            print(f"Erro ao calcular porcentagem do saldo operacional: {e}")
            return 0.0
    
    def can_open_new_positions(self):
        """
        Verifica se o usuário pode abrir novas posições
        Retorna: bool - True se pode abrir, False se bloqueado
        """
        try:
            # Verificar se é assinante (admin ou usuário especial)
            if self.is_admin:
                return True
            
            # Verificar margem de segurança (95%)
            usage_percentage = self.get_operational_balance_percentage()
            
            # Bloquear se atingiu 95% do saldo
            if usage_percentage >= 95.0:
                return False
            
            return True
            
        except Exception as e:
            print(f"Erro ao verificar se pode abrir posições: {e}")
            return False
    
    def get_remaining_balance_usd(self):
        """
        Calcula o saldo operacional restante em USD
        Retorna: float - Saldo restante (é o saldo atual mesmo)
        """
        try:
            # O saldo restante é simplesmente o saldo atual, pois as comissões já foram descontadas
            current_balance = getattr(self, 'operational_balance_usd', 0.0) or 0.0
            return max(current_balance, 0.0)  # Mínimo 0
            
        except Exception as e:
            print(f"Erro ao calcular saldo restante: {e}")
            return 0.0
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'api_configured': self.api_configured,
            'nautilus_trader_id': self.nautilus_trader_id, # Corrigido aqui
            'operational_balance': self.operational_balance,
            'operational_balance_usd': self.operational_balance_usd,
            'commission_rate': self.commission_rate,
            'can_open_positions': self.can_open_new_positions(),
            'operational_balance_percentage': self.get_operational_balance_percentage(),
            'remaining_balance_usd': self.get_remaining_balance_usd()
        }

    def __repr__(self):
        return f'<User {self.email}>'