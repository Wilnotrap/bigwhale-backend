from database import db
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import relationship

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
    
    # Relacionamento
    user = relationship('User', back_populates='sessions')
    
    def __init__(self, user_id, session_token, user_agent=None, ip_address=None, expires_in_hours=24):
        self.user_id = user_id
        self.session_token = session_token
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    def is_expired(self):
        """Verifica se a sessão expirou"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, hours=24):
        """Estende a sessão por mais X horas"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()
    
    def deactivate(self):
        """Desativa a sessão"""
        self.is_active = False
    
    def update_activity(self):
        """Atualiza o timestamp da última atividade"""
        self.last_activity = datetime.utcnow()
    
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
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Remove sessões expiradas do banco de dados"""
        expired_sessions = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            db.session.delete(session)
        
        db.session.commit()
        return len(expired_sessions)
    
    @classmethod
    def get_active_sessions_for_user(cls, user_id):
        """Retorna todas as sessões ativas para um usuário"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.is_active == True,
            cls.expires_at > datetime.utcnow()
        ).all()
    
    @classmethod
    def deactivate_all_user_sessions(cls, user_id):
        """Desativa todas as sessões de um usuário"""
        sessions = cls.query.filter(
            cls.user_id == user_id,
            cls.is_active == True
        ).all()
        
        for session in sessions:
            session.deactivate()
        
        db.session.commit()
        return len(sessions)
    
    def __repr__(self):
        return f'<UserSession {self.id} for User {self.user_id}>'