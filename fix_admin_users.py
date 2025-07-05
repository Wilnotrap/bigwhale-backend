from app import create_app
from database import db
from models.user import User
from werkzeug.security import generate_password_hash

def fix_admin_users():
    """Força a recriação/atualização dos usuários admin com credenciais corretas"""
    app = create_app()
    
    with app.app_context():
        try:
            # Usuários corretos
            admin_users = [
                {
                    'full_name': 'Admin Principal',
                    'email': 'admin@bwhale.site',
                    'password': 'Admin123!@#',
                    'is_admin': True
                },
                {
                    'full_name': 'Admin Teste', 
                    'email': 'teste@bwhale.site',
                    'password': 'Teste123!@#',
                    'is_admin': True
                },
                {
                    'full_name': 'Usuario Demo',
                    'email': 'demo@bwhale.site', 
                    'password': 'Demo123!@#',
                    'is_admin': False
                },
                {
                    'full_name': 'Admin BigWhale',
                    'email': 'admin@bigwhale.com',
                    'password': 'Raikamaster1@',
                    'is_admin': True
                }
            ]
            
            for user_data in admin_users:
                # Verificar se usuário existe
                user = User.query.filter_by(email=user_data['email']).first()
                
                if user:
                    # Atualizar usuário existente
                    user.full_name = user_data['full_name']
                    user.set_password(user_data['password'])
                    user.is_admin = user_data['is_admin']
                    user.is_active = True
                    user.has_paid = True
                    user.subscription_status = 'active'
                    user.payment_status = 'paid'
                    print(f"✅ Usuário {user_data['email']} ATUALIZADO")
                else:
                    # Criar novo usuário
                    user = User(
                        full_name=user_data['full_name'],
                        email=user_data['email'],
                        is_admin=user_data['is_admin'],
                        is_active=True,
                        has_paid=True,
                        subscription_status='active',
                        payment_status='paid'
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    print(f"✅ Usuário {user_data['email']} CRIADO")
                
                # Testar senha imediatamente
                if user.check_password(user_data['password']):
                    print(f"✅ Senha de {user_data['email']} VERIFICADA")
                else:
                    print(f"❌ ERRO: Senha de {user_data['email']} NÃO FUNCIONA")
            
            db.session.commit()
            print("\n🎉 TODOS OS USUÁRIOS CORRIGIDOS!")
            
            # Listar todos os usuários
            all_users = User.query.all()
            print("\n📋 USUÁRIOS NO BANCO:")
            for u in all_users:
                print(f"  - {u.email} (Admin: {u.is_admin}, Ativo: {u.is_active})")
                
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    fix_admin_users()