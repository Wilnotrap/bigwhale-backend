# create_admin_users.py - Script para criar usuários admin
from flask import Flask
from database import db
from models.user import User
from werkzeug.security import generate_password_hash
import os

# Configuração básica do Flask
app = Flask(__name__)

# Configuração do banco de dados SQLite para teste local
db_path = os.path.join(os.path.dirname(__file__), 'test_bigwhale.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['AES_ENCRYPTION_KEY'] = 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789'

# Inicializar banco
db.init_app(app)

def create_admin_users():
    """Cria os usuários admin no banco de dados"""
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        # Usuário 1: admin@bigwhale.com
        user1 = User.query.filter_by(email='admin@bigwhale.com').first()
        if not user1:
            user1 = User(
                full_name='Admin BigWhale',
                email='admin@bigwhale.com',
                password_hash=generate_password_hash('Raikamaster1@'),
                is_active=True,
                is_admin=True
            )
            db.session.add(user1)
            print("Usuário admin@bigwhale.com criado")
        else:
            # Atualizar senha se usuário já existe
            user1.password_hash = generate_password_hash('Raikamaster1@')
            print("Senha do usuário admin@bigwhale.com atualizada")
        
        # Usuário 2: willian@lexxusadm.com.br
        user2 = User.query.filter_by(email='willian@lexxusadm.com.br').first()
        if not user2:
            user2 = User(
                full_name='Willian Admin',
                email='willian@lexxusadm.com.br',
                password_hash=generate_password_hash('Bigwhale202021@'),
                is_active=True,
                is_admin=True
            )
            db.session.add(user2)
            print("Usuário willian@lexxusadm.com.br criado")
        else:
            # Atualizar senha se usuário já existe
            user2.password_hash = generate_password_hash('Bigwhale202021@')
            print("Senha do usuário willian@lexxusadm.com.br atualizada")
        
        # Salvar mudanças
        db.session.commit()
        
        # Verificar usuários criados
        total_users = User.query.count()
        print(f"\nTotal de usuários no banco: {total_users}")
        
        for user in User.query.all():
            print(f"- {user.email} (ativo: {user.is_active}, admin: {user.is_admin})")

if __name__ == '__main__':
    create_admin_users()