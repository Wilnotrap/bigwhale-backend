from ..database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_beta_user = db.Column(db.Boolean, default=False)
    has_access = db.Column(db.Boolean, default=True)
    payment_status = db.Column(db.String(50), default='pending')
    stripe_customer_id = db.Column(db.String(120), nullable=True)
    subscription_status = db.Column(db.String(50), default='inactive')
    subscription_id = db.Column(db.String(120), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'is_beta_user': self.is_beta_user,
            'has_access': self.has_access,
            'payment_status': self.payment_status,
            'stripe_customer_id': self.stripe_customer_id,
            'subscription_status': self.subscription_status,
            'subscription_id': self.subscription_id
        }