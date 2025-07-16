# backend/auth/routes.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.invite_code import InviteCode
from database import db
from utils.security import encrypt_api_key, decrypt_api_key
from api.bitget_client import BitgetAPI
from auth.login import login, logout, check_session
from services.nautilus_service import nautilus_service
import re # For password complexity
from flask_cors import cross_origin
from services.nautilus_service import NautilusService
from models.session import UserSession
from utils.api_persistence import api_persistence
import logging

# Criar blueprint para autenticação
auth_bp = Blueprint('auth', __name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password complexity: 8+ chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-])[A-Za-z\d@$!%*?&_\-]{8,}$')

# Códigos de convite
INVITE_CODE_LIMITED = "Bigwhale81#"  # Este terá limite de uso
INVITE_CODE_UNLIMITED = "Nautilus_big81#" # Este será ilimitado e hardcoded

# Função para validar complexidade da senha
def validate_password_complexity(password):
    """Valida se a senha atende aos critérios de complexidade"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r'\d', password):
        return False, "A senha deve conter pelo menos um número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "A senha deve conter pelo menos um caractere especial"
    
    return True, "Senha válida"

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def register():
    if request.method == 'OPTIONS':
        # Responder ao preflight request
        return '', 200
    try:
        # Obter dados do usuário
        data = request.get_json()
        
        # Validação básica de dados obrigatórios
        required_fields = ['full_name', 'email', 'password', 'bitget_api_key', 'bitget_api_secret', 'bitget_passphrase']
        missing_fields = []
        
        for field in required_fields:
            if not data.get(field) or not data.get(field).strip():
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'message': f'Campos obrigatórios faltando: {", ".join(missing_fields)}',
                'error_type': 'missing_fields',
                'missing_fields': missing_fields
            }), 400
        
        # Extrair dados
        full_name = data.get('full_name').strip()
        email = data.get('email').strip().lower()
        password = data.get('password')
        bitget_api_key = data.get('bitget_api_key').strip()
        bitget_api_secret = data.get('bitget_api_secret').strip()
        bitget_passphrase = data.get('bitget_passphrase').strip()
        
        # Validação adicional
        if len(password) < 6:
            return jsonify({
                'message': 'A senha deve ter pelo menos 6 caracteres',
                'error_type': 'password_too_short'
            }), 400
        
        # Validar formato do email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'message': 'Email inválido',
                'error_type': 'invalid_email'
            }), 400
        
        # Verificar se o email já está cadastrado
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'message': 'Este email já está cadastrado',
                'error_type': 'email_already_exists'
            }), 409
        
        print(f"📝 INICIANDO CADASTRO para: {full_name} ({email})")
        
        # Criptografar credenciais para o banco local
        print("🔐 Criptografando credenciais...")
        encrypted_key = encrypt_api_key(bitget_api_key)
        encrypted_secret = encrypt_api_key(bitget_api_secret)
        encrypted_passphrase = encrypt_api_key(bitget_passphrase)
        
        if not all([encrypted_key, encrypted_secret, encrypted_passphrase]):
            print("❌ Falha na criptografia")
            return jsonify({
                'message': 'Erro ao proteger credenciais da API',
                'error_type': 'encryption_error'
            }), 500
        
        print("✅ Credenciais criptografadas com sucesso")
        
        # Criar usuário
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            bitget_api_key_encrypted=encrypted_key,
            bitget_api_secret_encrypted=encrypted_secret,
            bitget_passphrase_encrypted=encrypted_passphrase,
            is_active=True
        )
        
        # Salvar no banco
        db.session.add(new_user)
        db.session.commit()

        print(f"✅ Usuário criado com sucesso: {new_user.id}")
        
        return jsonify({
            'message': 'Usuário registrado com sucesso! Faça login para continuar.',
            'user_id': new_user.id,
            'success': True
        }), 201

    except Exception as e:
        print(f"❌ ERRO na criação do usuário: {e}")
        db.session.rollback()
        
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'message': f'Erro durante criação do usuário: {str(e)}',
            'error_type': 'user_creation_error'
        }), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login_route():
    if request.method == 'OPTIONS':
        # Responder ao preflight request
        return '', 200
    return login()

@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def logout_route():
    if request.method == 'OPTIONS':
        return '', 200
    return logout()

@auth_bp.route('/session', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def session_route():
    if request.method == 'OPTIONS':
        return '', 200
    return check_session()

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    from flask import session
    
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    # Descriptografar as credenciais da API se existirem
    bitget_api_key = ''
    bitget_api_secret = ''
    bitget_passphrase = ''
    has_api_configured = False
    
    if user.bitget_api_key_encrypted and user.bitget_api_secret_encrypted and user.bitget_passphrase_encrypted:
        try:
            bitget_api_key = decrypt_api_key(user.bitget_api_key_encrypted) or ''
            bitget_api_secret = decrypt_api_key(user.bitget_api_secret_encrypted) or ''
            bitget_passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) or ''
            
            # Verificar se todas as credenciais foram descriptografadas com sucesso
            if bitget_api_key and bitget_api_secret and bitget_passphrase:
                has_api_configured = True
            else:
                print(f"⚠️ Credenciais incompletas após descriptografia para usuário {user.id}")
                
        except Exception as e:
            print(f"❌ Erro ao descriptografar credenciais da API para usuário {user.id}: {e}")
            # Se falhar na descriptografia, indicar que não tem API configurada
            has_api_configured = False
            bitget_api_key = ''
            bitget_api_secret = ''
            bitget_passphrase = ''

    # Retornar dados do perfil no formato esperado pelo frontend
    return jsonify({
        'user': {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'is_admin': user.is_admin,
            'is_active': user.is_active,
            'api_configured': has_api_configured,
            'bitget_api_key': bitget_api_key,
            'bitget_api_secret': bitget_api_secret,
            'bitget_passphrase': bitget_passphrase,
            'has_api_configured': has_api_configured,
            'api_status': 'active' if has_api_configured else 'not_configured'
        }
    }), 200

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Verifica o status da autenticação"""
    from flask import session
    
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                # Verificar se tem credenciais configuradas
                has_api_credentials = bool(
                    user.bitget_api_key_encrypted and 
                    user.bitget_api_secret_encrypted and 
                    user.bitget_passphrase_encrypted
                )
                
                return jsonify({
                    'authenticated': True,
                    'user_id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'api_configured': has_api_credentials
                }), 200
        
        return jsonify({'authenticated': False}), 200
        
    except Exception as e:
        return jsonify({'authenticated': False, 'error': str(e)}), 500