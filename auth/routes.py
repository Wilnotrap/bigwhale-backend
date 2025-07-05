# backend/auth/routes.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
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

INVITE_CODE = "Raikamaster202021@"

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

@auth_bp.route('/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
    data = request.get_json()

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    bitget_api_key = data.get('bitget_api_key')
    bitget_api_secret = data.get('bitget_api_secret')
    bitget_passphrase = data.get('bitget_passphrase')
    invite_code_attempt = data.get('invite_code') # Novo campo para o código de convite

    valor_entrada_padrao = data.get('valor_entrada_padrao', '')
    percentual_entrada_padrao = data.get('percentual_entrada_padrao', '')
    servidor_operacao = data.get('servidor_operacao', '')

    # --- Input Validation ---
    if not all([full_name, email, password, bitget_api_key, bitget_api_secret, bitget_passphrase]):
        return jsonify({'message': 'Todos os campos são obrigatórios, incluindo a Passphrase da Bitget'}), 400

    if not PASSWORD_REGEX.match(password):
        return jsonify({'message': 'A senha não atende aos requisitos de complexidade. Deve ter 8+ caracteres, incluir maiúscula, minúscula, número e caractere especial.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Endereço de email já registrado'}), 409 # Conflict

    # --- Verificação do Código de Convite (OBRIGATÓRIA) ---
    invite_code_used = bool(invite_code_attempt and invite_code_attempt == INVITE_CODE)
    if not invite_code_used:
        print(f"❌ Tentativa de registro sem código de convite válido: '{invite_code_attempt}'")
        return jsonify({'message': 'Código de convite obrigatório e inválido. Verifique se digitou corretamente.'}), 403
    
    print(f"✅ Código de convite válido fornecido: {invite_code_attempt}")

    # --- Create User ---
    try:
        # Criptografar as credenciais
        encrypted_key = encrypt_api_key(bitget_api_key)
        encrypted_secret = encrypt_api_key(bitget_api_secret)
        encrypted_passphrase = encrypt_api_key(bitget_passphrase)

        if not encrypted_key or not encrypted_secret or not encrypted_passphrase:
            return jsonify({'message': 'Falha ao proteger credenciais da API. Tente novamente.'}), 500

        new_user = User(
            full_name=full_name,
            email=email,
            bitget_api_key_encrypted=encrypted_key,
            bitget_api_secret_encrypted=encrypted_secret,
            bitget_passphrase_encrypted=encrypted_passphrase,
            is_active=True
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        success_message = 'Usuário registrado com sucesso! Faça login para continuar.'
        
        return jsonify({
            'message': success_message,
            'invite_code_used': invite_code_used
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao registrar usuário: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/login', methods=['POST'])
def login_route():
    return login()

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    return logout()

@auth_bp.route('/session', methods=['GET'])
def check_session_route():
    return check_session()