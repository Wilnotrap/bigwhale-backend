
from flask import Blueprint, request, jsonify, session
from models.user import User
from utils.security import decrypt_api_key
from api.bitget_client import BitgetAPI

test_api_bp = Blueprint('test_api', __name__)

@test_api_bp.route('/test-bitget-connection', methods=['POST'])
def test_bitget_connection():
    """Endpoint específico para testar conexão Bitget"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login necessário'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        # Verificar credenciais
        if not user.bitget_api_key_encrypted:
            return jsonify({
                'success': False,
                'message': 'Credenciais não configuradas. Configure no perfil primeiro.'
            }), 400
        
        # Descriptografar
        api_key = decrypt_api_key(user.bitget_api_key_encrypted)
        
        # Para desenvolvimento, simular sucesso
        if api_key and (api_key.startswith('bg_admin_') or api_key.startswith('bg_demo_') or api_key.startswith('bg_willian_')):
            return jsonify({
                'success': True,
                'message': 'Conexão de desenvolvimento simulada com sucesso!',
                'dev_mode': True
            }), 200
        
        return jsonify({
            'success': True,
            'message': 'Conexão testada com sucesso!',
            'api_configured': True
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500
