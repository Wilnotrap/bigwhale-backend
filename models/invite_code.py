from database import db
from datetime import datetime
from sqlalchemy import inspect

class InviteCode(db.Model):
    __tablename__ = 'invite_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(128), nullable=True)
    max_uses = db.Column(db.Integer, nullable=True)  # None = ilimitado
    used_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)

    def can_be_used(self):
        if self.max_uses is None:
            return True
        return self.used_count < self.max_uses

    def register_use(self):
        self.used_count += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<InviteCode {self.code} ({self.used_count}/{self.max_uses})>'

def initialize_invite_codes(app):
    with app.app_context():
        inspector = inspect(db.engine)
        if 'invite_codes' not in inspector.get_table_names():
            db.create_all()  # Cria todas as tabelas (incluindo invite_codes)
            print('Tabela invite_codes criada.')
        else:
            print('Tabela invite_codes já existe.')

        # Garante a existência do código Bigwhale81# com limite de 10 usos
        bigwhale_code = "Bigwhale81#"
        existing_bigwhale = InviteCode.query.filter_by(code=bigwhale_code).first()
        if not existing_bigwhale:
            invite = InviteCode(code=bigwhale_code, description="Convite padrão limitado (10 usos)", max_uses=10)
            db.session.add(invite)
            db.session.commit()
            print(f"Código de convite '{bigwhale_code}' criado com limite de 10 usos.")
        else:
            print(f"Código de convite '{bigwhale_code}' já existe.")

        # Remove o código Nautilus_big81# da tabela se ele por acaso existir (agora é hardcoded)
        nautilus_code = "Nautilus_big81#"
        existing_nautilus = InviteCode.query.filter_by(code=nautilus_code).first()
        if existing_nautilus:
            db.session.delete(existing_nautilus)
            db.session.commit()
            print(f"Código de convite '{nautilus_code}' removido da tabela (agora é hardcoded).") 