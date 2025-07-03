# test_models.py - Script para testar modelos e banco de dados
from flask import Flask, jsonify
from database import db
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

@app.route('/test-models', methods=['GET'])
def test_models():
    try:
        # Testar importação dos modelos
        from models.user import User
        from models.session import UserSession
        
        # Testar conexão com banco
        with app.app_context():
            # Criar tabelas se não existirem
            db.create_all()
            
            # Testar consulta simples
            user_count = User.query.count()
            session_count = UserSession.query.count()
            
            return jsonify({
                'status': 'success',
                'message': 'Modelos importados e banco conectado com sucesso',
                'user_count': user_count,
                'session_count': session_count,
                'database_path': app.config['SQLALCHEMY_DATABASE_URI']
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao testar modelos: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/test-login-simple', methods=['POST'])
def test_login_simple():
    try:
        from flask import request
        from models.user import User
        from werkzeug.security import check_password_hash
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar senha
        if not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Senha incorreta'}), 401
        
        return jsonify({
            'status': 'success',
            'message': 'Login realizado com sucesso',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro no login: {str(e)}',
            'error_type': type(e).__name__
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)