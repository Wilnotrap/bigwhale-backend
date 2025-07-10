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
import hashlib
import hmac
from datetime import datetime, timedelta

# Criar blueprint para autenticação
auth_bp = Blueprint('auth', __name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password complexity: 8+ chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-])[A-Za-z\d@$!%*?&_\-]{8,}$')

INVITE_CODE = "Bigwhale81#"

# Chave secreta para validar tokens de pagamento
PAYMENT_TOKEN_SECRET = "bigwhale_payment_secret_2024"

def generate_payment_token(email, session_id=None):
    """Gera um token de pagamento válido"""
    timestamp = datetime.now().timestamp()
    
    # Usar session_id padrão se não fornecido
    if not session_id:
        session_id = 'payment_confirmed'
    
    data = f"{email}:{session_id}:{timestamp}"
    token = hmac.new(
        PAYMENT_TOKEN_SECRET.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    print(f"🔑 Token gerado para {email} com session_id: {session_id}")
    return f"{token}:{timestamp}"

def verify_payment_token(token, email):
    """Verifica se o token de pagamento é válido"""
    try:
        if not token or ':' not in token:
            return False
            
        # Separar o token em partes: hash:timestamp
        token_hash, timestamp_str = token.rsplit(':', 1)
        timestamp = float(timestamp_str)
        
        # Verificar se o token não expirou (válido por 1 hora)
        if datetime.now().timestamp() - timestamp > 3600:
            return False
            
        # CORREÇÃO: Simplificar validação
        # Aceitar tokens gerados para este email e timestamp
        # O session_id pode ser qualquer string válida
        
        # Testar formatos comuns conhecidos
        common_session_ids = [
            'payment_confirmed', 
            'cs_test_simulate',
            'test123',
            'payment_success'
        ]
        
        for session_id in common_session_ids:
            expected_data = f"{email}:{session_id}:{timestamp}"
            expected_token = hmac.new(
                PAYMENT_TOKEN_SECRET.encode('utf-8'),
                expected_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(token_hash, expected_token):
                print(f"✅ Token válido encontrado com session_id: {session_id}")
                return True
        
        # Se não encontrou match, rejeitar por segurança
        print(f"❌ Token inválido - não encontrou match para email: {email}")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao validar token: {e}")
        return False

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
    payment_token = data.get('payment_token') # Token de pagamento confirmado

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

    # --- Verificação do Código de Convite OU Token de Pagamento ---
    invite_code_used = bool(invite_code_attempt and invite_code_attempt == INVITE_CODE)
    payment_confirmed = bool(payment_token and verify_payment_token(payment_token, email))
    
    # Aceitar registro se tiver código de convite válido OU pagamento confirmado
    if not invite_code_used and not payment_confirmed:
        print(f"❌ Tentativa de registro sem código de convite válido ou pagamento confirmado")
        print(f"   Código de convite: '{invite_code_attempt}'")
        print(f"   Token de pagamento: {'Válido' if payment_token else 'Ausente'}")
        return jsonify({'message': 'Código de convite obrigatório e inválido OU pagamento não confirmado. Verifique se digitou corretamente ou realize o pagamento.'}), 403
    
    if payment_confirmed:
        print(f"✅ Registro autorizado por pagamento confirmado para: {email}")
    else:
        print(f"✅ Código de convite válido fornecido: {invite_code_attempt}")

    # --- INTEGRAÇÃO NAUTILUS (OBRIGATÓRIA) ---
    # Tenta enviar os dados para o Nautilus antes de criar o usuário local.
    # Hipótese: O campo 'apiSecret' do Nautilus na verdade espera a 'passphrase'.
    print("🚀 Iniciando integração com sistema Nautilus...")
    
    user_data_for_nautilus = {
        'full_name': full_name,
        'email': email,
        'password': password,
        'bitget_api_key': bitget_api_key,
        'bitget_api_secret': bitget_passphrase, # ENVIANDO A PASSPHRASE NO LUGAR DO SECRET
        'bitget_passphrase': bitget_passphrase,
        'valor_entrada_padrao': valor_entrada_padrao,
        'percentual_entrada_padrao': percentual_entrada_padrao,
        'servidor_operacao': servidor_operacao
    }

    nautilus_token = None
    nautilus_user_id = None
    nautilus_connected = False
    nautilus_data_sent = False
    nautilus_error_details = None
    
    try:
        # 1. Obter credenciais do Nautilus
        print("Obtendo credenciais do sistema Nautilus...")
        nautilus_result = nautilus_service.get_nautilus_credentials()
        
        if nautilus_result['success']:
            nautilus_token = nautilus_result.get('token')
            nautilus_user_id = nautilus_result.get('nautilus_user_id')
            nautilus_connected = True
            print(f"Credenciais Nautilus obtidas com sucesso. Token: {nautilus_token[:20] if nautilus_token else 'N/A'}..., User ID: {nautilus_user_id}")
            
            # 2. Enviar dados do usuário para o Nautilus
            print("Enviando dados do usuário para o servidor Nautilus...")
            nautilus_send_result = nautilus_service.send_user_data_to_nautilus(user_data_for_nautilus)
            
            if nautilus_send_result['success']:
                nautilus_data_sent = True
                print("✅ Dados do usuário enviados para Nautilus com sucesso!")
            else:
                nautilus_error_details = nautilus_send_result.get('error')
                # Se o envio para o Nautilus falhar, o registro é interrompido.
                print(f"❌ Falha crítica ao enviar dados para Nautilus: {nautilus_error_details}")
                return jsonify({'message': f'Falha na comunicação com o servidor de integração: {nautilus_error_details}'}), 500
        else:
            nautilus_error_details = nautilus_result.get('error')
            print(f"❌ Falha crítica ao obter credenciais Nautilus: {nautilus_error_details}")
            return jsonify({'message': f'Não foi possível conectar ao servidor de integração: {nautilus_error_details}'}), 500
            
    except Exception as e:
        nautilus_error_details = f"Erro na integração Nautilus: {str(e)}"
        print(f"❌ Erro crítico na integração Nautilus: {nautilus_error_details}")
        return jsonify({'message': f'Ocorreu um erro inesperado durante a integração: {nautilus_error_details}'}), 500
    
    # --- Create User (SÓ OCORRE APÓS SUCESSO NO NAUTILUS) ---
    try:
        # 3. Criptografar as credenciais APENAS para o banco de dados LOCAL
        print("🔐 Iniciando processo de criptografia das credenciais para o banco de dados local...")
        encrypted_key = encrypt_api_key(bitget_api_key)
        encrypted_secret = encrypt_api_key(bitget_api_secret)
        encrypted_passphrase = encrypt_api_key(bitget_passphrase)
        print("✅ Credenciais criptografadas com sucesso para o banco de dados local.")

        if not encrypted_key or not encrypted_secret or not encrypted_passphrase:
            print("❌ Falha na criptografia das credenciais")
            return jsonify({'message': 'Falha ao proteger credenciais da API. Tente novamente.'}), 500

        print("👤 Criando novo usuário no banco de dados...")
        new_user = User(
            full_name=full_name,
            email=email,
            bitget_api_key_encrypted=encrypted_key,
            bitget_api_secret_encrypted=encrypted_secret,
            bitget_passphrase_encrypted=encrypted_passphrase,
            nautilus_token=nautilus_token, # Pode ser None se falhou
            nautilus_user_id=nautilus_user_id, # Pode ser None se falhou
            nautilus_active=nautilus_data_sent, # Define o status com base no sucesso do envio
            is_active=True # Activate after successful API validation
        )
        print("🔑 Definindo senha do usuário...")
        new_user.set_password(password)

        print("💾 Salvando usuário no banco de dados...")
        db.session.add(new_user)
        db.session.commit()
        print("✅ Usuário salvo com sucesso no banco de dados")

        # Mensagem personalizada baseada no resultado da integração
        api_status_msg = ""
        if nautilus_data_sent:
            if payment_confirmed:
                success_message = f'Usuário registrado com sucesso após pagamento confirmado! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
            elif invite_code_used:
                success_message = f'Usuário registrado com sucesso usando código de convite! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
            else:
                success_message = f'Usuário registrado com sucesso! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
        else:
            if payment_confirmed:
                success_message = f'Usuário registrado com sucesso após pagamento confirmado! Integração com Nautilus será tentada posteriormente.{api_status_msg} Faça login para continuar.'
            elif invite_code_used:
                success_message = f'Usuário registrado com sucesso usando código de convite! Integração com Nautilus será tentada posteriormente.{api_status_msg} Faça login para continuar.'
            else:
                success_message = f'Usuário registrado com sucesso! Integração com Nautilus será tentada posteriormente.{api_status_msg} Faça login para continuar.'
        
        return jsonify({
            'message': success_message,
            'nautilus_user_id': nautilus_user_id,
            'nautilus_connected': nautilus_connected,
            'nautilus_data_sent': nautilus_data_sent,
            'nautilus_error': nautilus_error_details if not nautilus_data_sent else None,
            'invite_code_used': invite_code_used,
            'payment_confirmed': payment_confirmed,
            'api_validation_enabled': False,
            'api_validation_success': False
        }), 201

    except Exception as e:
        db.session.rollback()
        # Log the exception e with more details
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERRO DURANTE O REGISTRO:")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(f"Traceback completo:\n{error_details}")
        return jsonify({
            'message': 'Ocorreu um erro durante o registro. Tente novamente.',
            'error_type': type(e).__name__,
            'error_details': str(e)
        }), 500

# Nova rota para gerar token de pagamento após webhook
@auth_bp.route('/generate-payment-token', methods=['POST'])
@cross_origin(supports_credentials=True)
def generate_payment_token_route():
    """Gera um token de pagamento válido após confirmação do webhook"""
    data = request.get_json()
    
    email = data.get('email')
    session_id = data.get('session_id', 'payment_confirmed')  # Usar padrão
    
    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400
    
    print(f"🎯 Gerando token de pagamento para: {email}")
    print(f"   Session ID: {session_id}")
    
    # Gerar token de pagamento
    token = generate_payment_token(email, session_id)
    
    return jsonify({
        'payment_token': token,
        'email': email,
        'session_id': session_id,
        'valid_until': (datetime.now() + timedelta(hours=1)).isoformat(),
        'message': 'Token de pagamento gerado com sucesso'
    }), 200

@auth_bp.route('/login', methods=['POST'])
def login_route():
    return login()

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    return logout()

@auth_bp.route('/session', methods=['GET'])
def session_route():
    return check_session()

@auth_bp.route('/logout-all', methods=['POST'])
def logout_all_sessions():
    """Endpoint para derrubar todas as sessões ativas"""
    from flask import session
    
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    try:
        # Desativar todas as sessões ativas no sistema (se existirem)
        cleared_sessions = 0
        try:
            cleared_sessions = UserSession.deactivate_all_sessions()
        except Exception as db_error:
            print(f"Erro ao acessar sessões no banco: {db_error}")
        
        # Limpar a sessão atual do Flask
        session.clear()
        
        return jsonify({
            'message': 'Todas as sessões foram encerradas com sucesso.',
            'sessions_cleared': cleared_sessions + 1,  # +1 para a sessão atual
            'success': True,
            'note': 'Flask sessions são isoladas por cliente. Esta ação limpa a sessão atual.'
        }), 200
        
    except Exception as e:
        print(f"Erro geral ao desativar sessões: {e}")
        # Mesmo se houver erro, limpar a sessão atual
        session.clear()
        
        return jsonify({
            'message': 'Sessão atual encerrada com sucesso.',
            'sessions_cleared': 1,
            'success': True
        }), 200

@auth_bp.route('/sessions', methods=['GET'])
def list_active_sessions():
    """Endpoint para listar sessões ativas (para debug/admin)"""
    from flask import session
    
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    try:
        # Buscar sessões ativas no banco (se existirem)
        active_sessions = []
        try:
            db_sessions = UserSession.query.filter_by(is_active=True).all()
            active_sessions = [s.to_dict() for s in db_sessions]
        except Exception as db_error:
            print(f"Erro ao buscar sessões no banco: {db_error}")
        
        # Informações da sessão atual
        current_session_info = {
            'current_session': {
                'user_id': session.get('user_id'),
                'session_active': True,
                'type': 'Flask Session'
            },
            'database_sessions': active_sessions,
            'total_sessions': len(active_sessions) + 1
        }
        
        return jsonify(current_session_info), 200
        
    except Exception as e:
        print(f"Erro ao listar sessões: {e}")
        return jsonify({
            'message': 'Erro ao listar sessões',
            'current_session': {
                'user_id': session.get('user_id'),
                'session_active': True,
                'type': 'Flask Session'
            },
            'database_sessions': [],
            'total_sessions': 1
        }), 200

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
    
    # Retornar dados do perfil incluindo as credenciais da API
    return jsonify({
        'user': {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'api_configured': has_api_configured,
            # Suportar ambos os nomes para compatibilidade total
            'api_key': bitget_api_key,
            'secret_key': bitget_api_secret,
            'passphrase': bitget_passphrase,
            'bitget_api_key': bitget_api_key,
            'bitget_api_secret': bitget_api_secret,  # Nome esperado pelo frontend
            'bitget_secret_key': bitget_api_secret,  # Nome atual do backend
            'bitget_passphrase': bitget_passphrase,
            'api_status': 'active' if has_api_configured else 'not_configured',
            'is_admin': user.is_admin,
            'is_active': user.is_active
        }
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    from flask import session
    
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    data = request.get_json()
    print(f"Dados recebidos na atualização de perfil: {data}")
    
    # Campos que podem ser atualizados
    full_name = data.get('full_name')
    email = data.get('email')
    # Suportar ambos os nomes de campos para compatibilidade
    bitget_api_key = data.get('api_key') or data.get('bitget_api_key')
    bitget_api_secret = data.get('secret_key') or data.get('bitget_api_secret')
    bitget_passphrase = data.get('passphrase') or data.get('bitget_passphrase')
    
    print(f"API Key atualizada: {bitget_api_key[:5] if bitget_api_key else 'N/A'}...")
    print(f"Secret key atualizada via bitget_api_secret: {bitget_api_secret[:5] if bitget_api_secret else 'N/A'}...")
    print(f"Passphrase atualizada: {'configurada' if bitget_passphrase else 'não fornecida'}")
    
    try:
        # Atualizar nome se fornecido
        if full_name:
            user.full_name = full_name
        
        # Atualizar email se fornecido e diferente do atual
        if email and email != user.email:
            # Verificar se o novo email já existe
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'message': 'Este email já está em uso'}), 409
            user.email = email
        
        # Atualizar credenciais da API Bitget se fornecidas
        api_updated = False
        if any([bitget_api_key, bitget_api_secret, bitget_passphrase]):
            # Se alguma credencial foi fornecida, todas devem ser fornecidas
            if not all([bitget_api_key, bitget_api_secret, bitget_passphrase]):
                return jsonify({'message': 'Todas as credenciais da API devem ser fornecidas (API Key, Secret e Passphrase)'}), 400
            
            # Fazer backup automático das credenciais atuais antes de atualizar
            try:
                api_persistence.auto_backup_on_update(user.id)
            except Exception as e:
                print(f"⚠️ Erro no backup automático para usuário {user.id}: {e}")
            print(f"🔄 Atualizando credenciais da API para usuário {user.id}")
            
            # Validar as novas credenciais usando o cliente Bitget
            try:
                bitget_client = BitgetAPI(
                    api_key=bitget_api_key.strip(), 
                    secret_key=bitget_api_secret.strip(),
                    passphrase=bitget_passphrase.strip()
                )
                
                # Validar as credenciais da API
                print(f"🔄 Validando credenciais da API para usuário {user.id}...")
                is_api_valid = bitget_client.validate_credentials()
                if not is_api_valid:
                    print(f"❌ Credenciais da API inválidas para usuário {user.id}")
                    return jsonify({'message': 'Credenciais da API Bitget inválidas. Verifique se estão corretas.'}), 400
                    
                print(f"✅ Credenciais da API validadas com sucesso para usuário {user.id}")
                
                # Criptografar e salvar as novas credenciais
                encrypted_key = encrypt_api_key(bitget_api_key.strip())
                encrypted_secret = encrypt_api_key(bitget_api_secret.strip())
                encrypted_passphrase = encrypt_api_key(bitget_passphrase.strip())
                
                if not encrypted_key or not encrypted_secret or not encrypted_passphrase:
                    print(f"❌ Falha na criptografia das credenciais para usuário {user.id}")
                    return jsonify({'message': 'Falha ao proteger credenciais da API'}), 500
                
                user.bitget_api_key_encrypted = encrypted_key
                user.bitget_api_secret_encrypted = encrypted_secret
                user.bitget_passphrase_encrypted = encrypted_passphrase
                api_updated = True
                
                # Verificar se as credenciais foram realmente salvas
                print(f"Status das chaves API:")
                print(f"  - API Key: {bool(user.bitget_api_key_encrypted)} - {user.bitget_api_key_encrypted[:5] if user.bitget_api_key_encrypted else 'N/A'}")
                print(f"  - Secret Key: {bool(user.bitget_api_secret_encrypted)} - {user.bitget_api_secret_encrypted[:5] if user.bitget_api_secret_encrypted else 'N/A'}")
                print(f"  - Passphrase: {bool(user.bitget_passphrase_encrypted)} - {'configurada' if user.bitget_passphrase_encrypted else 'não configurada'}")
                print(f"  - API configurada: {bool(user.bitget_api_key_encrypted and user.bitget_api_secret_encrypted and user.bitget_passphrase_encrypted)}")
                
                print(f"✅ Credenciais criptografadas e salvas para usuário {user.id}")
                
            except Exception as e:
                print(f"❌ Erro ao processar credenciais para usuário {user.id}: {e}")
                return jsonify({'message': f'Erro ao processar credenciais da API: {str(e)}'}), 500
        
        # Forçar flush para garantir que os dados sejam escritos
        db.session.flush()
        db.session.commit()
        print(f"Perfil atualizado para: {user.email}")
        
        # Verificar se as credenciais foram persistidas após o commit
        if api_updated:
            user_verificacao = User.query.get(user.id)
            credenciais_persistidas = bool(
                user_verificacao.bitget_api_key_encrypted and 
                user_verificacao.bitget_api_secret_encrypted and 
                user_verificacao.bitget_passphrase_encrypted
            )
            print(f"Verificação pós-commit - Credenciais persistidas: {credenciais_persistidas}")
            
            if not credenciais_persistidas:
                print(f"❌ FALHA CRÍTICA: Credenciais não foram persistidas para usuário {user.id}")
                # Tentar salvar novamente
                try:
                    user.bitget_api_key_encrypted = encrypt_api_key(bitget_api_key.strip())
                    user.bitget_api_secret_encrypted = encrypt_api_key(bitget_api_secret.strip())
                    user.bitget_passphrase_encrypted = encrypt_api_key(bitget_passphrase.strip())
                    db.session.commit()
                    print(f"✅ Segunda tentativa de salvamento bem-sucedida para usuário {user.id}")
                except Exception as retry_error:
                    print(f"❌ Falha na segunda tentativa de salvamento: {retry_error}")
        
        # Mensagem de sucesso personalizada
        message = 'Perfil atualizado com sucesso'
        if api_updated:
            message = 'Perfil e credenciais da API atualizados com sucesso! As credenciais estão agora ativas.'
        
        # Verificação final das credenciais salvas
        final_check = {
            'api_key_saved': bool(user.bitget_api_key_encrypted),
            'secret_saved': bool(user.bitget_api_secret_encrypted),
            'passphrase_saved': bool(user.bitget_passphrase_encrypted)
        }
        print(f"Verificação final antes de retornar: {final_check}")
        
        # Verificar credenciais descriptografadas para resposta
        final_api_key = ''
        final_secret_key = ''
        final_passphrase = ''
        api_configured_final = False
        
        if user.bitget_api_key_encrypted and user.bitget_api_secret_encrypted and user.bitget_passphrase_encrypted:
            try:
                final_api_key = decrypt_api_key(user.bitget_api_key_encrypted) or ''
                final_secret_key = decrypt_api_key(user.bitget_api_secret_encrypted) or ''
                final_passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) or ''
                api_configured_final = bool(final_api_key and final_secret_key and final_passphrase)
                print(f"✅ Credenciais descriptografadas com sucesso para resposta")
            except Exception as e:
                print(f"❌ Erro ao descriptografar para resposta: {e}")
        
        return jsonify({
            'message': message,
            'success': True,
            'api_configured': api_configured_final,
            'credentials_saved': all(final_check.values()),
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'api_configured': api_configured_final,
                'api_status': 'active' if api_configured_final else 'not_configured',
                'api_updated': api_updated,
                'has_api_credentials': api_configured_final,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar perfil: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Verifica o status da autenticação"""
    from flask import session
    
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                return jsonify({
                    'authenticated': True,
                    'user_id': user.id,
                    'email': user.email,
                    'full_name': user.full_name
                }), 200
        
        return jsonify({'authenticated': False}), 200
        
    except Exception as e:
        return jsonify({'authenticated': False, 'error': str(e)}), 500

# TODO: Add 2FA setup and verification routes
# TODO: Add password reset functionality

# Placeholder for Bitget API interaction (to be moved to api/bitget_client.py or similar)
# class BitgetAPI:
#     def __init__(self, api_key, secret_key, passphrase):
#         self.api_key = api_key
#         self.secret_key = secret_key
#         self.passphrase = passphrase # Bitget might require a passphrase for API

#     def validate_credentials(self):
#         # This method would make a simple API call to Bitget to verify credentials
#         # Example: fetch account balance or a non-sensitive endpoint
#         # Return True if valid, False otherwise
#         print(f"Validating API Key: {self.api_key[:5]}... Secret: {self.secret_key[:5]}...")
#         # Simulate API call
#         # In a real scenario, use 'requests' or a Bitget SDK
#         # For now, assume valid if keys are not empty
#         return bool(self.api_key and self.secret_key)