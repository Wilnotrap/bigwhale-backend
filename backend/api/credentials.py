# backend/api/credentials.py
from flask import Blueprint, jsonify, session
from models.user import User
from utils.security import decrypt_api_key
import logging

# Criar blueprint para credenciais
credentials_bp = Blueprint('credentials', __name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@credentials_bp.route('/status', methods=['GET'])
def get_credentials_status():
    """Endpoint para verificar status das credenciais da API"""
    
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        return jsonify({
            'message': 'Usuário não autenticado',
            'api_configured': False
        }), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({
            'message': 'Usuário não encontrado',
            'api_configured': False
        }), 404
    
    try:
        # Verificar se o usuário tem credenciais salvas
        has_credentials = bool(
            user.bitget_api_key_encrypted and 
            user.bitget_api_secret_encrypted and 
            user.bitget_passphrase_encrypted
        )
        
        if not has_credentials:
            return jsonify({
                'api_configured': False,
                'message': 'Credenciais da API não configuradas',
                'has_credentials': False
            }), 200
        
        # Tentar descriptografar as credenciais para verificar se estão válidas
        try:
            api_key = decrypt_api_key(user.bitget_api_key_encrypted)
            api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
            passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)
            
            # Verificar se a descriptografia foi bem-sucedida
            if api_key and api_secret and passphrase:
                return jsonify({
                    'api_configured': True,
                    'has_credentials': True,
                    'message': 'Credenciais configuradas e válidas',
                    'credentials': {
                        'api_key': api_key,
                        'secret_key': api_secret,
                        'passphrase': passphrase
                    }
                }), 200
            else:
                logger.error(f"Falha na descriptografia das credenciais para usuário {user.id}")
                return jsonify({
                    'api_configured': False,
                    'has_credentials': True,
                    'message': 'Erro ao descriptografar credenciais',
                    'error': 'decryption_failed'
                }), 500
                
        except Exception as decrypt_error:
            logger.error(f"Erro na descriptografia para usuário {user.id}: {decrypt_error}")
            return jsonify({
                'api_configured': False,
                'has_credentials': True,
                'message': 'Erro ao acessar credenciais',
                'error': str(decrypt_error)
            }), 500
        
    except Exception as e:
        logger.error(f"Erro ao verificar status das credenciais para usuário {user.id}: {e}")
        return jsonify({
            'api_configured': False,
            'message': 'Erro interno ao verificar credenciais',
            'error': str(e)
        }), 500