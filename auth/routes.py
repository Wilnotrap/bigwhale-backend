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

@auth_bp.route('/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
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
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'message': 'Email inválido',
                'error_type': 'invalid_email'
            }), 400
        
        # Validar credenciais da API
        if len(bitget_api_key) < 10:
            return jsonify({
                'message': 'API Key deve ter pelo menos 10 caracteres',
                'error_type': 'invalid_api_key'
            }), 400
        
        if len(bitget_api_secret) < 10:
            return jsonify({
                'message': 'API Secret deve ter pelo menos 10 caracteres',
                'error_type': 'invalid_api_secret'
            }), 400
        
        if len(bitget_passphrase) < 3:
            return jsonify({
                'message': 'Passphrase deve ter pelo menos 3 caracteres',
                'error_type': 'invalid_passphrase'
            }), 400
        
        # Verificar se o email já está cadastrado
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'message': 'Este email já está cadastrado',
                'error_type': 'email_already_exists'
            }), 409
        
        print(f"📝 INICIANDO CADASTRO para: {full_name} ({email})")
        
        # Validar credenciais da API com a Bitget ANTES de criar o usuário
        print(f"🔐 VALIDANDO CREDENCIAIS DA API...")
        try:
            from api.bitget_client import BitgetAPI
            
            # MODO DE DESENVOLVIMENTO: Aceitar credenciais de teste
            is_test_credentials = (
                bitget_api_key.startswith('bg_test_') or 
                bitget_api_key.startswith('bg_demo_') or
                'test' in bitget_api_key.lower() or
                'demo' in bitget_api_key.lower()
            )
            
            if is_test_credentials:
                print(f"🧪 MODO TESTE: Credenciais de teste detectadas para {email}")
                print(f"✅ CREDENCIAIS DE TESTE ACEITAS para {email}")
                is_api_valid = True
            else:
                bitget_client = BitgetAPI(
                    api_key=bitget_api_key,
                    secret_key=bitget_api_secret,
                    passphrase=bitget_passphrase
                )
                
                # Testar credenciais reais
                print(f"🧪 Testando credenciais da API...")
                is_api_valid = bitget_client.validate_credentials()
                
                if not is_api_valid:
                    print(f"❌ CREDENCIAIS INVÁLIDAS para {email}")
                    return jsonify({
                        'message': 'Credenciais da API Bitget inválidas. Verifique se estão corretas e têm as permissões necessárias.',
                        'error_type': 'invalid_api_credentials'
                    }), 400
                
                print(f"✅ CREDENCIAIS VÁLIDAS para {email}")
                
                # Obter informações básicas da conta para confirmar
                account_info = bitget_client.get_account_balance()
                if not account_info:
                    print(f"❌ ERRO AO OBTER INFORMAÇÕES DA CONTA para {email}")
                    return jsonify({
                        'message': 'Não foi possível obter informações da conta. Verifique se as credenciais têm as permissões necessárias.',
                        'error_type': 'api_connection_error'
                    }), 400
                
                print(f"✅ CONTA VERIFICADA para {email}")
            
        except Exception as e:
            print(f"❌ ERRO NA VALIDAÇÃO DA API: {str(e)}")
            return jsonify({
                'message': f'Erro ao validar credenciais da API: {str(e)}',
                'error_type': 'api_validation_error'
            }), 400

    except Exception as e:
        print(f"❌ ERRO ao processar dados iniciais: {e}")
        return jsonify({
            'message': 'Erro ao processar dados da requisição',
            'error_type': 'request_processing_error',
            'error_details': str(e)
        }), 400

    # Avançar para a integração Nautilus e criação do usuário
    try:
        # Obter o código de convite e flag de pagamento dos dados originais
        invite_code_attempt = data.get('invite_code', '')
        paid_user = data.get('paid_user', False)
        
        # Campos opcionais para a integração Nautilus
        valor_entrada_padrao = data.get('valor_entrada_padrao', '')
        percentual_entrada_padrao = data.get('percentual_entrada_padrao', '')
        servidor_operacao = data.get('servidor_operacao', '')
        
        print(f"📝 Processando cadastro: {full_name} ({email})")
        print(f"🔑 Credenciais API válidas: ✅")
        print(f"🎫 Código convite: {invite_code_attempt}")
        print(f"💰 Usuário pagante: {paid_user}")
        
        invite_code_obj = None
        invite_code_used = False

        if paid_user:
            print("💰 USUÁRIO PAGANTE: Dispensando código de convite")
            invite_code_used = True
        elif invite_code_attempt == INVITE_CODE_UNLIMITED: # Código ilimitado da equipe
            print(f"✅ Código de convite ilimitado válido (equipe): {INVITE_CODE_UNLIMITED}")
            invite_code_used = True
        else: # Tentar validar código limitado pelo banco
            invite_code_obj = InviteCode.query.filter_by(code=invite_code_attempt).first()
            if not invite_code_obj or not invite_code_obj.can_be_used():
                print(f"❌ Código de convite inválido ou esgotado: '{invite_code_attempt}'")
                return jsonify({
                    'message': 'Código de convite obrigatório, inválido ou já atingiu o limite de uso. Verifique ou solicite outro código.',
                    'error_type': 'invalid_invite_code'
                }), 403
            invite_code_used = True
            print(f"✅ Código de convite limitado válido: {invite_code_attempt}")

        # Preparar dados para integração Nautilus
        user_data_for_nautilus = {
            'full_name': full_name,
            'email': email,
            'password': password,
            'bitget_api_key': bitget_api_key,
            'bitget_api_secret': bitget_api_secret,
            'bitget_passphrase': bitget_passphrase,
            'valor_entrada_padrao': valor_entrada_padrao,
            'percentual_entrada_padrao': percentual_entrada_padrao,
            'servidor_operacao': servidor_operacao
        }

        print("🚀 INTEGRAÇÃO NAUTILUS")
        print("-" * 50)
        
        # Integração com Nautilus
        nautilus_token = None
        nautilus_user_id = None
        nautilus_data_sent = False
        
        try:
            # Obter credenciais do Nautilus
            nautilus_result = nautilus_service.get_nautilus_credentials()
            
            if nautilus_result['success']:
                nautilus_token = nautilus_result.get('token')
                nautilus_user_id = nautilus_result.get('nautilus_user_id')
                print(f"✅ Credenciais Nautilus obtidas")
                
                # Enviar dados para o Nautilus
                nautilus_send_result = nautilus_service.send_user_data_to_nautilus(user_data_for_nautilus)
                
                if nautilus_send_result['success']:
                    nautilus_data_sent = True
                    print("✅ Dados enviados para Nautilus com sucesso")
                else:
                    error_msg = nautilus_send_result.get('error', 'Erro desconhecido')
                    print(f"❌ Erro ao enviar dados para Nautilus: {error_msg}")
                    
                    # Verificar se é erro de duplicata
                    if "já existem no sistema" in error_msg:
                        return jsonify({
                            'message': 'Email ou credenciais já cadastrados. Faça login ou entre em contato com o suporte.',
                            'error_type': 'duplicate_user'
                        }), 409
                    
                    return jsonify({
                        'message': f'Erro na integração: {error_msg}',
                        'error_type': 'nautilus_integration_error'
                    }), 500
            else:
                error_msg = nautilus_result.get('error', 'Erro desconhecido')
                print(f"❌ Erro ao obter credenciais Nautilus: {error_msg}")
                return jsonify({
                    'message': f'Erro de conectividade: {error_msg}',
                    'error_type': 'nautilus_connection_error'
                }), 500
                
        except Exception as e:
            print(f"❌ Erro crítico na integração Nautilus: {e}")
            return jsonify({
                'message': f'Erro interno na integração: {str(e)}',
                'error_type': 'nautilus_exception'
            }), 500

        print("👤 CRIAÇÃO DO USUÁRIO")
        print("-" * 50)
        
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
            nautilus_token=nautilus_token,
            nautilus_user_id=nautilus_user_id,
            nautilus_active=nautilus_data_sent,
            is_active=True
        )
        
        # Salvar no banco
        db.session.add(new_user)
        db.session.commit()
        
        # Se usou código de convite limitado, registrar uso APÓS commit (cadastro concluído)
        if invite_code_obj:
            invite_code_obj.register_use()

        print(f"✅ Usuário criado com sucesso: {new_user.id}")
        
        # Verificar se as credenciais foram salvas
        user_check = User.query.get(new_user.id)
        credentials_saved = bool(
            user_check.bitget_api_key_encrypted and 
            user_check.bitget_api_secret_encrypted and 
            user_check.bitget_passphrase_encrypted
        )
        
        print(f"✅ Verificação pós-criação - Credenciais salvas: {credentials_saved}")
        
        return jsonify({
            'message': 'Usuário registrado com sucesso! Credenciais API configuradas. Faça login para continuar.',
            'user_id': new_user.id,
            'credentials_configured': credentials_saved,
            'nautilus_integration': nautilus_data_sent,
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
                user.api_configured = True  # <-- ADICIONADO
                api_updated = True
                
                # Verificar se as credenciais foram realmente salvas
                final_check = {
                    'api_key': bool(user.bitget_api_key_encrypted),
                    'api_secret': bool(user.bitget_api_secret_encrypted),
                    'passphrase': bool(user.bitget_passphrase_encrypted)
                }
                print(f"Status das chaves API: {final_check}")

            except Exception as e:
                db.session.rollback()
                print(f"Erro ao validar/atualizar credenciais da API: {e}")
                return jsonify({'message': f'Erro ao validar/atualizar credenciais da API: {str(e)}'}), 500
        
        db.session.commit()
        message = 'Perfil atualizado com sucesso!'
        if api_updated:
            message += ' Credenciais da API atualizadas e validadas.'

        # Buscar e retornar dados do usuário atualizados
        user = User.query.get(session['user_id'])
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