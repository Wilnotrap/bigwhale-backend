# listar_credenciais_db.py
import os
import sys
from dotenv import load_dotenv
from flask import Flask

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def listar_credenciais():
    # Cria uma instância mínima do aplicativo Flask
    app = Flask(__name__)

    # Configura o caminho absoluto para o banco de dados SQLite
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_file_path = os.path.join(current_dir, 'backend', 'instance', 'site.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654')

    # Importa a instância global do SQLAlchemy AQUI
    # E inicializa ela com o app
    from backend.database import db 
    db.init_app(app)

    # Entra no contexto do aplicativo Flask
    with app.app_context():
        # Garante que o diretório 'backend' esteja no sys.path
        # para que os módulos internos (models, utils) possam ser importados corretamente.
        backend_path = os.path.join(current_dir, 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        # Importa os modelos e utilitários que dependem de 'db' DENTRO do contexto
        # Isso garante que eles vejam a instância de 'db' já inicializada com 'app'
        from backend.models.user import User
        from backend.utils.security import decrypt_api_key

        print("--- Listando Credenciais da API dos Usuários ---")
        
        users = User.query.all()
        
        if not users:
            print("Nenhum usuário encontrado no banco de dados.")
            return

        for user in users:
            print(f"\nUsuário ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Nome Completo: {user.full_name}")
            
            api_key_encrypted = user.bitget_api_key_encrypted
            api_secret_encrypted = user.bitget_api_secret_encrypted
            passphrase_encrypted = user.bitget_passphrase_encrypted

            if api_key_encrypted and api_secret_encrypted and passphrase_encrypted:
                try:
                    # Descriptografar as credenciais
                    api_key = decrypt_api_key(api_key_encrypted)
                    api_secret = decrypt_api_key(api_secret_encrypted)
                    passphrase = decrypt_api_key(passphrase_encrypted)

                    print(f"  API Key: {api_key if api_key else '[ERRO DE DESCRIPTOGRAFIA]'}")
                    print(f"  API Secret: {api_secret if api_secret else '[ERRO DE DESCRIPTOGRAFIA]'}")
                    print(f"  Passphrase: {passphrase if passphrase else '[ERRO DE DESCRIPTOGRAFIA]'}")
                    print("  Status: Credenciais encontradas e descriptografadas.")
                except Exception as e:
                    print(f"  Status: Erro ao descriptografar credenciais: {e}")
                    print(f"  API Key Criptografada: {api_key_encrypted[:20]}...")
                
            else:
                print("  Status: Nenhuma credencial de API Bitget salva para este usuário.")
        print("\n--- Fim da Listagem ---")

if __name__ == "__main__":
    listar_credenciais() 