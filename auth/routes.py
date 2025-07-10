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
from datetime import datetime

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

@auth_bp.route('/check-email', methods=['OPTIONS'])
@cross_origin(supports_credentials=True)
def check_email_options():
    """Handle preflight requests for CORS"""
    return '', 200

@auth_bp.route('/check-email', methods=['POST'])
@cross_origin(supports_credentials=True)
def check_email():
    """Verifica se o email já está registrado"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'message': 'Email é obrigatório'}), 400
            
        # Verificar se o email já existe
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            return jsonify({
                'available': False,
                'message': 'Este email já está registrado'
            }), 200
        else:
            return jsonify({
                'available': True,
                'message': 'Email disponível'
            }), 200
            
    except Exception as e:
        logger.error(f"Erro ao verificar email: {str(e)}")
        return jsonify({
            'message': 'Erro ao verificar email',
            'error': str(e)
        }), 500

@auth_bp.route('/users', methods=['GET'])
@cross_origin(supports_credentials=True)
def list_users():
    """Lista usuários existentes (para debug)"""
    try:
        users = User.query.all()
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else 'N/A'
            })
        
        return jsonify({
            'users': user_list,
            'count': len(user_list),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@auth_bp.route('/debug', methods=['GET'])
@cross_origin(supports_credentials=True)
def debug_info():
    """Endpoint para debug das configurações do servidor"""
    try:
        from flask import current_app
        
        debug_data = {
            'environment': 'Render',
            'cors_origins': [
                "https://bwhale.site",
                "http://bwhale.site",
                "https://www.bwhale.site",
                "http://www.bwhale.site"
            ],
            'invite_code_required': INVITE_CODE,
            'timestamp': datetime.now().isoformat(),
            'database_connected': False,
                         'user_count': 0,
             'payment_test_enabled': True
        }
        
        # Verificar conexão com banco
        try:
            user_count = User.query.count()
            debug_data['database_connected'] = True
            debug_data['user_count'] = user_count
        except Exception as db_error:
            debug_data['database_error'] = str(db_error)
        
        # Endpoint de teste de pagamento está habilitado
        debug_data['payment_test_enabled'] = True
        
        return jsonify(debug_data), 200
        
    except Exception as e:
        logger.error(f"Erro no debug: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@auth_bp.route('/register', methods=['OPTIONS'])
@cross_origin(supports_credentials=True)
def register_options():
    """Handle preflight requests for CORS"""
    return '', 200

@auth_bp.route('/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
    try:
        # Log da requisição recebida
        logger.info(f"=== NOVA TENTATIVA DE REGISTRO ===")
        logger.info(f"Origem da requisição: {request.headers.get('Origin', 'N/A')}")
        logger.info(f"User-Agent: {request.headers.get('User-Agent', 'N/A')}")
        
        data = request.get_json()
        
        if not data:
            logger.warning("Dados JSON não recebidos na requisição")
            return jsonify({'message': 'Dados não fornecidos'}), 400

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
        
        # Verificar se vem do pagamento aprovado
        payment_success = data.get('payment_success', False) or request.args.get('payment_success', False)
        
        logger.info(f"Dados recebidos - Email: {email}, Nome: {full_name}, Código de convite: {invite_code_attempt}, Pagamento aprovado: {payment_success}")

        # --- Input Validation ---
        if not all([full_name, email, password, bitget_api_key, bitget_api_secret, bitget_passphrase]):
            logger.warning("Campos obrigatórios ausentes")
            return jsonify({'message': 'Todos os campos são obrigatórios, incluindo a Passphrase da Bitget'}), 400

        if not PASSWORD_REGEX.match(password):
            logger.warning("Senha não atende aos critérios de complexidade")
            return jsonify({'message': 'A senha não atende aos requisitos de complexidade. Deve ter 8+ caracteres, incluir maiúscula, minúscula, número e caractere especial.'}), 400

        # Verificar se o email já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            logger.warning(f"Tentativa de registro com email já existente: {email}")
            return jsonify({'message': 'Endereço de email já registrado'}), 409 # Conflict

        # --- Verificação do Código de Convite (OPCIONAL PARA PAGAMENTO APROVADO) ---
        invite_code_used = bool(invite_code_attempt and invite_code_attempt == INVITE_CODE)
        
        # Se veio do pagamento aprovado, pular verificação do código de convite
        if payment_success:
            logger.info(f"✅ Usuário vem do pagamento aprovado - código de convite não necessário")
            invite_code_required = False
        else:
            invite_code_required = True
            
        if invite_code_required and not invite_code_used:
            logger.warning(f"Código de convite inválido fornecido: '{invite_code_attempt}' (esperado: '{INVITE_CODE}')")
            return jsonify({
                'message': 'Código de convite obrigatório e inválido. Verifique se digitou corretamente.',
                'required_code': 'Raikamaster202021@',
                'received_code': invite_code_attempt
            }), 403
        
        if invite_code_used:
            logger.info(f"✅ Código de convite válido fornecido: {invite_code_attempt}")
        elif payment_success:
            logger.info(f"✅ Registro autorizado via pagamento aprovado")
        else:
            logger.warning("Nenhuma autorização válida para registro")

        # --- INTEGRAÇÃO NAUTILUS (OBRIGATÓRIA) ---
        # Tenta enviar os dados para o Nautilus antes de criar o usuário local.
        # Hipótese: O campo 'apiSecret' do Nautilus na verdade espera a 'passphrase'.
        logger.info("🚀 Iniciando integração com sistema Nautilus...")
        
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
            logger.info("Obtendo credenciais do sistema Nautilus...")
            nautilus_result = nautilus_service.get_nautilus_credentials()
            
            if nautilus_result['success']:
                nautilus_token = nautilus_result.get('token')
                nautilus_user_id = nautilus_result.get('nautilus_user_id')
                nautilus_connected = True
                logger.info(f"Credenciais Nautilus obtidas com sucesso. Token: {nautilus_token[:20] if nautilus_token else 'N/A'}..., User ID: {nautilus_user_id}")
                
                # 2. Enviar dados do usuário para o Nautilus
                logger.info("Enviando dados do usuário para o servidor Nautilus...")
                nautilus_send_result = nautilus_service.send_user_data_to_nautilus(user_data_for_nautilus)
                
                if nautilus_send_result['success']:
                    nautilus_data_sent = True
                    logger.info("✅ Dados do usuário enviados para Nautilus com sucesso!")
                else:
                    nautilus_error_details = nautilus_send_result.get('error')
                    # Se o envio para o Nautilus falhar, o registro é interrompido.
                    logger.error(f"❌ Falha crítica ao enviar dados para Nautilus: {nautilus_error_details}")
                    return jsonify({'message': f'Falha na comunicação com o servidor de integração: {nautilus_error_details}'}), 500
            else:
                nautilus_error_details = nautilus_result.get('error')
                logger.error(f"❌ Falha crítica ao obter credenciais Nautilus: {nautilus_error_details}")
                return jsonify({'message': f'Não foi possível conectar ao servidor de integração: {nautilus_error_details}'}), 500
                
        except Exception as e:
            nautilus_error_details = f"Erro na integração Nautilus: {str(e)}"
            logger.error(f"❌ Erro crítico na integração Nautilus: {nautilus_error_details}")
            return jsonify({'message': f'Ocorreu um erro inesperado durante a integração: {nautilus_error_details}'}), 500
        
        # --- Create User (SÓ OCORRE APÓS SUCESSO NO NAUTILUS) ---
        try:
            # 3. Criptografar as credenciais APENAS para o banco de dados LOCAL
            logger.info("🔐 Iniciando processo de criptografia das credenciais para o banco de dados local...")
            encrypted_key = encrypt_api_key(bitget_api_key)
            encrypted_secret = encrypt_api_key(bitget_api_secret)
            encrypted_passphrase = encrypt_api_key(bitget_passphrase)
            logger.info("✅ Credenciais criptografadas com sucesso para o banco de dados local.")

            if not encrypted_key or not encrypted_secret or not encrypted_passphrase:
                logger.error("❌ Falha na criptografia das credenciais")
                return jsonify({'message': 'Falha ao proteger credenciais da API. Tente novamente.'}), 500

            logger.info("👤 Criando novo usuário no banco de dados...")
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
            logger.info("🔑 Definindo senha do usuário...")
            new_user.set_password(password)

            logger.info("💾 Salvando usuário no banco de dados...")
            db.session.add(new_user)
            db.session.commit()
            logger.info("✅ Usuário salvo com sucesso no banco de dados")

            # Mensagem personalizada baseada no resultado da integração
            api_status_msg = ""
            if nautilus_data_sent:
                if payment_success:
                    success_message = f'Usuário registrado com sucesso após pagamento aprovado! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
                elif invite_code_used:
                    success_message = f'Usuário registrado com sucesso usando código de convite! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
                else:
                    success_message = f'Usuário registrado com sucesso! Dados enviados para o sistema Nautilus.{api_status_msg} Faça login para continuar.'
            else:
                if payment_success:
                    success_message = f'Usuário registrado com sucesso após pagamento aprovado! Integração com Nautilus será tentada posteriormente.{api_status_msg} Faça login para continuar.'
                elif invite_code_used:
                    success_message = f'Usuário registrado com sucesso usando código de convite! Integração com Nautilus será tentada posteriormente.{api_status_msg} Faça login para continuar.'
                else:
                    success_message = f'Usuário registrado com sucesso! Integração com Nautilus será tentada posteriormente.{api_status_msg} Faça login para continuar.'
            
            logger.info(f"✅ Registro concluído com sucesso para {email}")
            return jsonify({
                'message': success_message,
                'nautilus_user_id': nautilus_user_id,
                'nautilus_connected': nautilus_connected,
                'nautilus_data_sent': nautilus_data_sent,
                'nautilus_error': nautilus_error_details if not nautilus_data_sent else None,
                'invite_code_used': invite_code_used,
                'payment_success': payment_success,
                'registration_method': 'payment' if payment_success else 'invite_code' if invite_code_used else 'unknown',
                'api_validation_enabled': False,
                'api_validation_success': False
            }), 201

        except Exception as e:
            db.session.rollback()
            # Log the exception e with more details
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"❌ ERRO DURANTE O REGISTRO:")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            logger.error(f"Mensagem: {str(e)}")
            logger.error(f"Traceback completo:\n{error_details}")
            return jsonify({
                'message': 'Ocorreu um erro durante o registro. Tente novamente.',
                'error_type': type(e).__name__,
                'error_details': str(e)
            }), 500
            
    except Exception as global_error:
        logger.error(f"❌ ERRO GLOBAL NO REGISTRO: {str(global_error)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'message': 'Erro interno do servidor. Tente novamente.',
            'error': str(global_error)
        }), 500

@auth_bp.route('/register-payment-test', methods=['POST'])
@cross_origin(supports_credentials=True)
def register_payment_test():
    """Endpoint para testar registro via pagamento (simula pagamento aprovado)"""
    try:
        data = request.get_json()
        
        # Simular pagamento aprovado
        data['payment_success'] = True
        
        # Usar dados de teste se não fornecidos
        if not data.get('full_name'):
            data['full_name'] = 'Usuário Teste Pagamento'
        if not data.get('email'):
            data['email'] = f'teste.pagamento.{datetime.now().timestamp()}@bigwhale.com'
        if not data.get('password'):
            data['password'] = 'TestePagamento123@'
        if not data.get('bitget_api_key'):
            data['bitget_api_key'] = 'test_api_key_pagamento'
        if not data.get('bitget_api_secret'):
            data['bitget_api_secret'] = 'test_api_secret_pagamento'
        if not data.get('bitget_passphrase'):
            data['bitget_passphrase'] = 'test_passphrase_pagamento'
        
        logger.info(f"🧪 Testando registro via pagamento para: {data['email']}")
        
        # Processar como registro normal, mas com payment_success=True
        return register_internal(data)
        
    except Exception as e:
        logger.error(f"Erro no teste de pagamento: {str(e)}")
        return jsonify({
            'message': 'Erro no teste de pagamento',
            'error': str(e)
        }), 500

def register_internal(data):
    """Função interna para processar registro (reutilizada pelo teste)"""
    try:
        # Replicar a lógica do register mas usando data diretamente
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        bitget_api_key = data.get('bitget_api_key')
        bitget_api_secret = data.get('bitget_api_secret')
        bitget_passphrase = data.get('bitget_passphrase')
        invite_code_attempt = data.get('invite_code')
        payment_success = data.get('payment_success', False)
        
        logger.info(f"🔄 Processando registro interno - Email: {email}, Pagamento: {payment_success}")
        
        # Verificar se o email já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            logger.warning(f"Tentativa de registro com email já existente: {email}")
            return jsonify({'message': 'Endereço de email já registrado'}), 409
        
        # Verificação do código de convite (opcional para pagamento)
        invite_code_used = bool(invite_code_attempt and invite_code_attempt == INVITE_CODE)
        
        if payment_success:
            logger.info(f"✅ Registro via pagamento aprovado - código de convite não necessário")
            invite_code_required = False
        else:
            invite_code_required = True
            
        if invite_code_required and not invite_code_used:
            logger.warning(f"Código de convite inválido: '{invite_code_attempt}'")
            return jsonify({
                'message': 'Código de convite obrigatório e inválido. Verifique se digitou corretamente.',
                'required_code': 'Raikamaster202021@',
                'received_code': invite_code_attempt
            }), 403
        
        # Criptografar credenciais
        encrypted_key = encrypt_api_key(bitget_api_key)
        encrypted_secret = encrypt_api_key(bitget_api_secret)
        encrypted_passphrase = encrypt_api_key(bitget_passphrase)
        
        # Criar usuário
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
        
        logger.info(f"✅ Usuário criado com sucesso: {email}")
        
        return jsonify({
            'message': 'Usuário registrado com sucesso após pagamento aprovado!',
            'payment_success': payment_success,
            'registration_method': 'payment' if payment_success else 'invite_code' if invite_code_used else 'unknown',
            'user_id': new_user.id,
            'email': new_user.email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro no registro interno: {str(e)}")
        return jsonify({
            'message': 'Erro interno no registro',
            'error': str(e)
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
    
    # Usar o serviço de credenciais para carregar dados da API
    from services.api_credentials_service import APICredentialsService
    api_service = APICredentialsService()
    
    bitget_api_key = ''
    bitget_api_secret = ''
    bitget_passphrase = ''
    has_api_configured = False
    
    try:
        credentials = api_service.load_user_credentials(user_id=user.id)
        
        if credentials and credentials.get('has_credentials') and credentials.get('is_valid'):
            bitget_api_key = credentials.get('api_key', '')
            bitget_api_secret = credentials.get('api_secret', '')
            bitget_passphrase = credentials.get('passphrase', '')
            has_api_configured = True
            print(f"✅ Credenciais da API carregadas com sucesso para usuário {user.id}")
        else:
            print(f"⚠️ Usuário {user.id} não possui credenciais da API válidas")
            
    except Exception as e:
        print(f"❌ Erro ao carregar credenciais da API para usuário {user.id}: {e}")
        # Se falhar no carregamento, indicar que não tem API configurada
        has_api_configured = False
    
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
            
            # Usar o serviço de credenciais para validar e salvar
            try:
                from services.api_credentials_service import APICredentialsService
                api_service = APICredentialsService()
                
                print(f"🔄 Salvando credenciais da API para usuário {user.id}...")
                
                save_result = api_service.save_credentials(
                    user_id=user.id,
                    api_key=bitget_api_key,
                    api_secret=bitget_api_secret,
                    passphrase=bitget_passphrase,
                    validate=True
                )
                
                if not save_result['success']:
                    print(f"❌ Falha ao salvar credenciais: {save_result.get('error')}")
                    return jsonify({'message': save_result.get('error', 'Erro ao salvar credenciais da API')}), 400
                
                api_updated = True
                print(f"✅ Credenciais da API salvas com sucesso para usuário {user.id}")
                
            except Exception as e:
                print(f"❌ Erro ao processar credenciais da API: {e}")
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

@auth_bp.route('/sync-credentials', methods=['POST'])
def sync_credentials():
    """
    Endpoint para sincronizar/recarregar credenciais da API baseado no email
    Útil para garantir que as credenciais estejam sempre disponíveis após o login
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'message': 'Email é obrigatório'}), 400
            
        # Usar o serviço de credenciais para sincronizar
        from services.api_credentials_service import APICredentialsService
        api_service = APICredentialsService()
        
        result = api_service.sync_credentials_by_email(email)
        
        if not result['success']:
            return jsonify({
                'message': result.get('error', 'Erro na sincronização'),
                'success': False
            }), 400
            
        credentials = result.get('credentials', {})
        
        return jsonify({
            'message': result.get('message', 'Credenciais sincronizadas com sucesso'),
            'success': True,
            'credentials': {
                'user_id': credentials.get('user_id'),
                'email': credentials.get('email'),
                'has_credentials': credentials.get('has_credentials', False),
                'is_valid': credentials.get('is_valid', False),
                'api_validated': credentials.get('api_validated', False)
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao sincronizar credenciais: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/api-status', methods=['GET'])
def get_api_status():
    """
    Endpoint para verificar o status das credenciais da API do usuário logado
    """
    from flask import session
    
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    try:
        from services.api_credentials_service import APICredentialsService
        api_service = APICredentialsService()
        
        user_id = session['user_id']
        api_status = api_service.get_user_api_status(user_id)
        
        # Carregar credenciais completas se existirem
        credentials = api_service.load_user_credentials(user_id=user_id)
        
        response_data = {
            'success': True,
            'api_status': api_status,
            'credentials': {
                'has_credentials': credentials.get('has_credentials', False) if credentials else False,
                'is_valid': credentials.get('is_valid', False) if credentials else False,
                'user_id': user_id
            }
        }
        
        # Se as credenciais estão válidas, incluir informações básicas (sem as chaves reais)
        if credentials and credentials.get('is_valid'):
            response_data['credentials'].update({
                'api_key_configured': bool(credentials.get('api_key')),
                'api_secret_configured': bool(credentials.get('api_secret')),
                'passphrase_configured': bool(credentials.get('passphrase'))
            })
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Erro ao verificar status da API: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/reload-credentials', methods=['POST'])
def reload_credentials():
    """
    Endpoint para forçar o recarregamento das credenciais da API do usuário logado
    """
    from flask import session
    
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    try:
        from services.api_credentials_service import APICredentialsService
        api_service = APICredentialsService()
        
        user_id = session['user_id']
        
        # Carregar credenciais do usuário
        credentials = api_service.load_user_credentials(user_id=user_id)
        
        if not credentials:
            return jsonify({
                'message': 'Não foi possível carregar credenciais',
                'success': False
            }), 400
            
        if not credentials.get('has_credentials'):
            return jsonify({
                'message': 'Usuário não possui credenciais da API configuradas',
                'success': True,
                'credentials': {
                    'has_credentials': False,
                    'is_valid': False
                }
            }), 200
            
        # Validar credenciais
        is_valid = api_service.validate_credentials(credentials)
        
        return jsonify({
            'message': 'Credenciais recarregadas com sucesso',
            'success': True,
            'credentials': {
                'has_credentials': credentials.get('has_credentials', False),
                'is_valid': credentials.get('is_valid', False),
                'api_validated': is_valid,
                'user_id': user_id
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao recarregar credenciais: {e}")
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