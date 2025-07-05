# backend/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # API keys criptografadas
    bitget_api_key_encrypted = db.Column(db.Text, nullable=True)
    bitget_api_secret_encrypted = db.Column(db.Text, nullable=True)
    bitget_passphrase_encrypted = db.Column(db.Text, nullable=True)
    
    # Status e configurações
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Campos de pagamento/assinatura
    has_paid = db.Column(db.Boolean, default=False, nullable=False)
    subscription_type = db.Column(db.String(50), nullable=True)
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    payment_status = db.Column(db.String(50), default='pending')
    subscription_status = db.Column(db.String(50), default='inactive')
    
    # Saldo operacional
    operational_balance = db.Column(db.Float, default=0.0)
    operational_balance_usd = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Taxa de comissão
    commission_rate = db.Column(db.Float, default=0.35)

    # Relacionamento com trades
    trades = relationship('Trade', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        """Criptografa e define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta"""
        return check_password_hash(self.password_hash, password)
    
    def is_subscription_active(self):
        """Verifica se a assinatura está ativa"""
        if not self.has_paid or not self.subscription_end_date:
            return False
        return datetime.utcnow() <= self.subscription_end_date
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'has_paid': self.has_paid,
            'subscription_active': self.is_subscription_active(),
            'subscription_type': self.subscription_type,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'payment_status': self.payment_status,
            'stripe_customer_id': self.stripe_customer_id,
            'subscription_status': self.subscription_status,
            'subscription_id': self.stripe_subscription_id
        }

    def __repr__(self):
        return f'<User {self.email}>'