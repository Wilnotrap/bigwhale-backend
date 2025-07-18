from backend.database import db
from backend.models.invite_code import InviteCode
from backend.app import app
from sqlalchemy import inspect

def create_invite_codes():
    inspector = inspect(db.engine)
    if 'invite_codes' not in inspector.get_table_names():
        InviteCode.__table__.create(db.engine)
        print('Tabela invite_codes criada.')
    else:
        print('Tabela invite_codes já existe.')

    codes = [
        {"code": "Bigwhale81#", "description": "Convite padrão limitado (10 usos)", "max_uses": 10},
        {"code": "Nautilus_big81#", "description": "Convite equipe ilimitado", "max_uses": None},
    ]
    for c in codes:
        existing = InviteCode.query.filter_by(code=c["code"]).first()
        if not existing:
            invite = InviteCode(code=c["code"], description=c["description"], max_uses=c["max_uses"])
            db.session.add(invite)
    db.session.commit()
    print("Códigos de convite criados/atualizados com sucesso!")

if __name__ == "__main__":
    with app.app_context():
        create_invite_codes() 