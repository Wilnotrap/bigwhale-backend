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

INVITE_CODE = "Bigwhale81#"

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
    try:
        print("🚀 INÍCIO DO PROCESSO DE REGISTRO")
        data = request.get_json()
        print(f"📥 Dados recebidos: {list(data.keys()) if data else 'None'}")

        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        bitget_api_key = data.get('bitget_api_key')
        bitget_api_secret = data.get('bitget_api_secret')
        bitget_passphrase = data.get('bitget_passphrase')
        invite_code_attempt = data.get('invite_code') # Novo campo para o código de convite
        paid_user = data.get('paid_user', False) # Flag para usuários que já pagaram via Stripe
        
        print(f"📝 Dados extraídos: nome={bool(full_name)}, email={bool(email)}, senha={bool(password)}")
        print(f"🔑 Credenciais API: key={bool(bitget_api_key)}, secret={bool(bitget_api_secret)}, pass={bool(bitget_passphrase)}")
        print(f"🎫 Código convite: {bool(invite_code_attempt)}")
        print(f"💰 Usuário pagante: {paid_user}")
    except Exception as e:
        print(f"❌ ERRO ao processar dados iniciais: {e}")
        return jsonify({
            'message': 'Erro ao processar dados da requisição',
            'error_type': 'request_processing_error',
            'error_details': str(e)
        }), 400

    try:
        print("🔍 INICIANDO VALIDAÇÕES")
        valor_entrada_padrao = data.get('valor_entrada_padrao', '')
        percentual_entrada_padrao = data.get('percentual_entrada_padrao', '')
        servidor_operacao = data.get('servidor_operacao', '')

        # --- Input Validation ---
        print("📋 Validando campos obrigatórios...")
        if not all([full_name, email, password, bitget_api_key, bitget_api_secret, bitget_passphrase]):
            print("❌ Campos obrigatórios faltando")
            return jsonify({'message': 'Todos os campos são obrigatórios, incluindo a Passphrase da Bitget'}), 400

        print("🔐 Validando complexidade da senha...")
        if not PASSWORD_REGEX.match(password):
            print("❌ Senha não atende aos requisitos")
            return jsonify({'message': 'A senha não atende aos requisitos de complexidade. Deve ter 8+ caracteres, incluir maiúscula, minúscula, número e caractere especial.'}), 400

        print("📧 Verificando se email já existe...")
        if User.query.filter_by(email=email).first():
            print(f"❌ Email já registrado: {email}")
            return jsonify({'message': 'Endereço de email já registrado'}), 409 # Conflict

        # --- Verificação do Código de Convite OU Pagamento ---
        print("🎫 Validando código de convite ou pagamento...")
        
        if paid_user:
            # Usuário já pagou via Stripe - dispensar código de convite
            print("💰 USUÁRIO PAGANTE: Dispensando código de convite (pagamento confirmado)")
            invite_code_used = True  # Considerar como se tivesse código válido
        else:
            # Usuário precisa do código de convite
            invite_code_used = bool(invite_code_attempt and invite_code_attempt == INVITE_CODE)
            if not invite_code_used:
                print(f"❌ Código de convite inválido: '{invite_code_attempt}' (esperado: '{INVITE_CODE}')")
                return jsonify({'message': 'Código de convite obrigatório e inválido. Verifique se digitou corretamente ou realize o pagamento via Stripe.'}), 403
            
            print(f"✅ Código de convite válido: {invite_code_attempt}")
        
        print("✅ TODAS AS VALIDAÇÕES PASSARAM")
        
    except Exception as e:
        print(f"❌ ERRO durante validações: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'message': 'Erro durante validação dos dados',
            'error_type': 'validation_error',
            'error_details': str(e)
        }), 500

    # --- INTEGRAÇÃO NAUTILUS (OBRIGATÓRIA) ---
    # Tenta enviar os dados para o Nautilus antes de criar o usuário local.
    # Hipótese: O campo 'apiSecret' do Nautilus na verdade espera a 'passphrase'.
    print("🚀 Iniciando integração com sistema Nautilus...")
    
    user_data_for_nautilus = {
        'full_name': full_name,
        'email': email,
        'password': password,
        'bitget_api_key': bitget_api_key,
        'bitget_api_secret': bitget_api_secret,  # CORRIGIDO: Enviando o secret correto
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
            print("📤 ENDPOINT - Enviando dados do usuário para o servidor Nautilus...")
            nautilus_send_result = nautilus_service.send_user_data_to_nautilus(user_data_for_nautilus)
            
            print("=" * 60)
            print("🔍 ENDPOINT - RESULTADO DO NAUTILUS:")
            print("=" * 60)
            print(f"📊 Success: {nautilus_send_result.get('success')}")
            print(f"📝 Message: {nautilus_send_result.get('message')}")
            print(f"❌ Error: {nautilus_send_result.get('error')}")
            print(f"🏷️ Error Type: {nautilus_send_result.get('error_type')}")
            print(f"📄 Details: {nautilus_send_result.get('details')}")
            print(f"🆔 Nautilus User ID: {nautilus_send_result.get('nautilus_user_created_id')}")
            print("=" * 60)
            
            if nautilus_send_result['success']:
                nautilus_data_sent = True
                print("✅ ENDPOINT - Dados do usuário enviados para Nautilus com SUCESSO!")
                print("🎯 ENDPOINT - Continuando para criação do usuário local...")
            else:
                nautilus_error_details = nautilus_send_result.get('error')
                print(f"❌ ENDPOINT - FALHA ao enviar dados para Nautilus: {nautilus_error_details}")
                
                # Melhorar mensagem para casos de duplicata
                if "já existem no sistema Nautilus" in nautilus_error_details:
                    user_message = "Este email ou suas credenciais da Bitget já estão cadastrados no sistema. Se você já possui uma conta, faça login. Se esqueceu sua senha, entre em contato com o suporte."
                    error_code = 409  # Conflict
                else:
                    user_message = f'Erro na comunicação com o servidor de integração: {nautilus_error_details}'
                    error_code = 500
                
                print(f"🚨 ENDPOINT - Retornando erro {error_code} para o frontend")
                return jsonify({
                    'message': user_message,
                    'error_type': 'nautilus_send_error',
                    'error_details': nautilus_error_details
                }), error_code
        else:
            nautilus_error_details = nautilus_result.get('error')
            print(f"❌ FALHA CRÍTICA ao obter credenciais Nautilus: {nautilus_error_details}")
            return jsonify({
                'message': f'Não foi possível conectar ao servidor de integração: {nautilus_error_details}',
                'error_type': 'nautilus_auth_error',
                'error_details': nautilus_error_details
            }), 500
            
    except Exception as e:
        nautilus_error_details = f"Erro na integração Nautilus: {str(e)}"
        print(f"❌ ERRO CRÍTICO na integração Nautilus: {nautilus_error_details}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'message': f'Ocorreu um erro inesperado durante a integração: {nautilus_error_details}',
            'error_type': 'nautilus_exception',
            'error_details': str(e)
        }), 500
    
    # --- Create User (SÓ OCORRE APÓS SUCESSO NO NAUTILUS) ---
    try:
        # 3. Criptografar as credenciais APENAS para o banco de dados LOCAL
        print("🔐 INICIANDO CRIPTOGRAFIA das credenciais...")
        print(f"🔑 Criptografando API Key (length: {len(bitget_api_key) if bitget_api_key else 0})")
        encrypted_key = encrypt_api_key(bitget_api_key)
        print(f"✅ API Key criptografada: {bool(encrypted_key)}")
        
        print(f"🔒 Criptografando API Secret (length: {len(bitget_api_secret) if bitget_api_secret else 0})")
        encrypted_secret = encrypt_api_key(bitget_api_secret)
        print(f"✅ API Secret criptografado: {bool(encrypted_secret)}")
        
        print(f"🔐 Criptografando Passphrase (length: {len(bitget_passphrase) if bitget_passphrase else 0})")
        encrypted_passphrase = encrypt_api_key(bitget_passphrase)
        print(f"✅ Passphrase criptografado: {bool(encrypted_passphrase)}")

        if not encrypted_key or not encrypted_secret or not encrypted_passphrase:
            print(f"❌ FALHA na criptografia: key={bool(encrypted_key)}, secret={bool(encrypted_secret)}, pass={bool(encrypted_passphrase)}")
            return jsonify({
                'message': 'Falha ao proteger credenciais da API. Verifique se todas as credenciais foram fornecidas.',
                'error_type': 'encryption_error'
            }), 500

        print("👤 CRIANDO OBJETO USUÁRIO...")
        print(f"📊 Dados do usuário: nautilus_token={bool(nautilus_token)}, nautilus_user_id={nautilus_user_id}, nautilus_active={nautilus_data_sent}")
        
        new_user = User(
            full_name=full_name,
            email=email,
            bitget_api_key_encrypted=encrypted_key,
            bitget_api_secret_encrypted=encrypted_secret,
            bitget_passphrase_encrypted=encrypted_passphrase,
            nautilus_token=nautilus_token,
            nautilus_user_id=nautilus_user_id,
            nautilus_active=nautilus_data_sent,
            is_active=True
        )
        print("✅ Objeto usuário criado com sucesso")
        
        print("🔑 DEFININDO SENHA do usuário...")
        new_user.set_password(password)
        print("✅ Senha definida com sucesso")

        print("💾 SALVANDO no banco de dados...")
        db.session.add(new_user)
        print("📝 Usuário adicionado à sessão")
        
        db.session.commit()
        print("✅ COMMIT realizado - Usuário salvo no banco!")

        # Mensagem personalizada baseada no resultado da integração
        api_status_msg = ""
        if nautilus_data_sent:
            if paid_user:
                success_message = f'Usuário registrado com sucesso após pagamento confirmado! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
            elif invite_code_used:
                success_message = f'Usuário registrado com sucesso usando código de convite! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
            else:
                success_message = f'Usuário registrado com sucesso! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
        else:
            if paid_user:
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
            'api_validation_enabled': False,
            'api_validation_success': False
        }), 201

    except Exception as e:
        print("🚨 EXCEÇÃO CAPTURADA no bloco de criação do usuário!")
        db.session.rollback()
        print("↩️ Rollback executado")
        
        # Log detalhado do erro
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERRO DURANTE A CRIAÇÃO DO USUÁRIO:")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        print(f"📝 Mensagem: {str(e)}")
        print(f"📊 Traceback completo:\n{error_details}")
        
        # Identificar categoria do erro
        error_category = "unknown"
        if "IntegrityError" in str(type(e)):
            error_category = "database_constraint"
        elif "OperationalError" in str(type(e)):
            error_category = "database_operation" 
        elif "AttributeError" in str(type(e)):
            error_category = "object_attribute"
        elif "TypeError" in str(type(e)):
            error_category = "type_error"
        
        return jsonify({
            'message': f'Erro durante criação do usuário: {str(e)}',
            'error_type': type(e).__name__,
            'error_category': error_category,
            'error_details': str(e),
            'stage': 'user_creation'
        }), 500

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