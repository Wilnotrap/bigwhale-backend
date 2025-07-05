from database import db
from datetime import datetime, timedelta
import uuid

class UserSession(db.Model):
    """Model para rastrear sessões ativas dos usuários"""
    
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    
    # Relationship
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def __init__(self, user_id, session_token, user_agent=None, ip_address=None, expires_in_hours=24):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.session_token = session_token
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        self.is_active = True
    
    def is_expired(self):
        """Verifica se a sessão expirou"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """Converte a sessão para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address
        }
    
    def __repr__(self):
        return f'<UserSession {self.id} for User {self.user_id}>'