# Nautilus Backend Models
from flask_sqlalchemy import SQLAlchemy

# Instância global do SQLAlchemy
db = SQLAlchemy()

# Importar todos os modelos
from .user import User
from .trade import Trade
from .session import Session
from .invite_code import InviteCode

__all__ = ['db', 'User', 'Trade', 'Session', 'InviteCode']