from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Usar a string de conexão do backend (Render/Heroku padrão)
DB_PATH = os.environ.get('DATABASE_URL')
if not DB_PATH:
    raise Exception('A variável de ambiente DATABASE_URL não está definida!')
engine = create_engine(DB_PATH)
Base = declarative_base()

class InviteCode(Base):
    __tablename__ = 'invite_codes'
    id = Column(Integer, primary_key=True)
    code = Column(String(64), unique=True, nullable=False)
    description = Column(String(128), nullable=True)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

Session = sessionmaker(bind=engine)
session = Session()

def create_table_and_codes():
    Base.metadata.create_all(engine)
    print('Tabela invite_codes criada ou já existe.')
    codes = [
        {"code": "Bigwhale81#", "description": "Convite padrão limitado (10 usos)", "max_uses": 10},
        {"code": "Nautilus_big81#", "description": "Convite equipe ilimitado", "max_uses": None},
    ]
    for c in codes:
        existing = session.query(InviteCode).filter_by(code=c["code"]).first()
        if not existing:
            invite = InviteCode(code=c["code"], description=c["description"], max_uses=c["max_uses"])
            session.add(invite)
    session.commit()
    print("Códigos de convite criados/atualizados com sucesso!")

if __name__ == "__main__":
    create_table_and_codes() 