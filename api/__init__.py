# backend/api/__init__.py
from flask import Blueprint, request, jsonify, session
from models.user import User
from database import db
from utils.security import encrypt_api_key, decrypt_api_key

api_credentials_bp = Blueprint('api_credentials', __name__)

@api_credentials_bp.route('/credentials', methods=['GET'])
def get_api_credentials():
    # Verifica se o usuário está autenticado
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    # Retorna as credenciais CRIPTOGRAFADAS para feedback visual
    api_key = user.bitget_api_key_encrypted or ''
    api_secret = user.bitget_api_secret_encrypted or ''
    passphrase = user.bitget_passphrase_encrypted or ''
    api_configured = bool(api_key and api_secret and passphrase)
    return jsonify({
        'api_configured': api_configured,
        'bitget_api_key': api_key,
        'bitget_api_secret': api_secret,
        'bitget_passphrase': passphrase
    }), 200

@api_credentials_bp.route('/credentials', methods=['POST'])
def save_api_credentials():
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    data = request.get_json()
    api_key = data.get('bitget_api_key', '').strip()
    api_secret = data.get('bitget_api_secret', '').strip()
    passphrase = data.get('bitget_passphrase', '').strip()
    if not (api_key and api_secret and passphrase):
        return jsonify({'message': 'Todos os campos de credenciais são obrigatórios'}), 400
    # Criptografa e salva
    user.bitget_api_key_encrypted = encrypt_api_key(api_key)
    user.bitget_api_secret_encrypted = encrypt_api_key(api_secret)
    user.bitget_passphrase_encrypted = encrypt_api_key(passphrase)
    db.session.commit()
    return jsonify({'message': 'Credenciais salvas com sucesso'}), 200