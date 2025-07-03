# backend/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
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
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relacionamentos
    sessions = relationship('UserSession', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Define a senha do usuário (hash)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o usuário para dicionário (sem dados sensíveis)"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def has_api_credentials(self):
        """Verifica se o usuário tem credenciais de API configuradas"""
        return bool(self.bitget_api_key_encrypted and 
                   self.bitget_api_secret_encrypted and 
                   self.bitget_passphrase_encrypted)
    
    def __repr__(self):
        return f'<User {self.email}>'