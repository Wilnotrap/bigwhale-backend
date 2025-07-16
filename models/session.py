from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid

# Instância compartilhada do SQLAlchemy
db = SQLAlchemy()

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
    
    def update_activity(self):
        """Atualiza o timestamp da última atividade"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def deactivate(self):
        """Desativa a sessão"""
        self.is_active = False
        db.session.commit()
    
    @classmethod
    def create_session(cls, user_id, user_agent=None, ip_address=None):
        """Cria uma nova sessão para o usuário"""
        session_token = str(uuid.uuid4())
        session = cls(
            user_id=user_id,
            session_token=session_token,
            user_agent=user_agent,
            ip_address=ip_address
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    @classmethod
    def get_active_session(cls, session_token):
        """Busca uma sessão ativa pelo token"""
        session = cls.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if session and not session.is_expired():
            session.update_activity()
            return session
        elif session and session.is_expired():
            session.deactivate()
        
        return None
    
    @classmethod
    def get_user_sessions(cls, user_id, active_only=True):
        """Busca todas as sessões de um usuário"""
        query = cls.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.all()
    
    @classmethod
    def deactivate_all_user_sessions(cls, user_id):
        """Desativa todas as sessões de um usuário"""
        sessions = cls.query.filter_by(user_id=user_id, is_active=True).all()
        
        for session in sessions:
            session.is_active = False
        
        db.session.commit()
        return len(sessions)
    
    @classmethod
    def deactivate_all_sessions(cls):
        """Desativa todas as sessões ativas no sistema"""
        sessions = cls.query.filter_by(is_active=True).all()
        
        for session in sessions:
            session.is_active = False
        
        db.session.commit()
        return len(sessions)
    
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