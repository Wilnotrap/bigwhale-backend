#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Corrigido - Sistema Bitget
Versão corrigida para resolver erro 500 no login
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from database import db

import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta, datetime

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def create_app(config_name='default'):
    """
    Cria e configura a aplicação Flask (Padrão App Factory).
    """
    # Adiciona o diretório 'backend' ao path para resolver importações relativas
    import sys
    sys.path.append(os.path.dirname(__file__))

    app = Flask(__name__, instance_relative_config=True)
    
    # --- Configuração de Logging ---
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nautilus.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Nautilus startup')
    
    # --- Configuração da Aplicação ---
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'),
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True,  # True para produção com HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=86400,  # 24 horas
        AES_ENCRYPTION_KEY=os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    )
    
    # Configuração do banco de dados SQLite
    # No Render, usar /tmp para arquivos temporários
    if os.environ.get('RENDER'):
        db_path = '/tmp/site.db'
    else:
        # Criar diretório instance se não existir
        instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir, exist_ok=True)
        db_path = os.path.join(instance_dir, 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- Inicialização de Extensões ---
    # Configuração CORS mais permissiva para produção, incluindo o domínio da Hostinger
    CORS(app, 
         supports_credentials=True, 
         origins=[
             "http://localhost:3000", 
             "http://localhost:3001", 
             "http://localhost:3002", 
             "http://127.0.0.1:3000", 
             "http://127.0.0.1:3001", 
             "http://127.0.0.1:3002",
             "https://bwhale.site",
             "http://bwhale.site"
         ],
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    db.init_app(app)
    
    # --- Função para garantir credenciais de admin ---
    def ensure_admin_credentials():
        """Garante que as credenciais de admin estejam corretas na inicialização"""
        try:
            from models.user import User
            from werkzeug.security import generate_password_hash
            
            # Credenciais padrão
            admin_users = [
                {
                    'email': 'admin@bigwhale.com',
                    'password': 'Raikamaster1@',
                    'full_name': 'Admin BigWhale',
                    'is_admin': True
                },
                {
                    'email': 'willian@lexxusadm.com.br',
                    'password': 'Bigwhale202021@',
                    'full_name': 'Willian Admin',
                    'is_admin': True
                }
            ]
            
            for admin_data in admin_users:
                user = User.query.filter_by(email=admin_data['email']).first()
                
                if user:
                    # Atualizar senha e status de admin se necessário
                    if not user.check_password(admin_data['password']):
                        user.password_hash = generate_password_hash(admin_data['password'])
                        user.is_active = True
                        app.logger.info(f"Credenciais atualizadas para {admin_data['email']}")
                    
                    # Garantir que o status de admin esteja correto
                    if user.is_admin != admin_data['is_admin']:
                        user.is_admin = admin_data['is_admin']
                        app.logger.info(f"Status de admin atualizado para {admin_data['email']}: {admin_data['is_admin']}")
                else:
                    # Criar usuário se não existir
                    user = User(
                        full_name=admin_data['full_name'],
                        email=admin_data['email'],
                        password_hash=generate_password_hash(admin_data['password']),
                        is_active=True,
                        is_admin=admin_data['is_admin']
                    )
                    db.session.add(user)
                    app.logger.info(f"Usuário {admin_data['email']} criado")
            
            db.session.commit()
            app.logger.info("Credenciais de admin configuradas com sucesso")
            
        except Exception as e:
            app.logger.error(f"Erro ao configurar credenciais de admin: {e}")
    
    # --- Login Simplificado ---
    @app.route('/api/auth/login', methods=['POST'])
    def login_simple():
        """Endpoint de login simplificado sem dependências complexas"""
        try:
            app.logger.info("=== INÍCIO DO LOGIN SIMPLIFICADO ===")
            
            # Verificar se a requisição contém JSON
            if not request.is_json:
                app.logger.error("Requisição não contém JSON válido")
                return jsonify({'message': 'Content-Type deve ser application/json'}), 400
                
            data = request.get_json()
            if not data:
                app.logger.error("Dados JSON vazios ou inválidos")
                return jsonify({'message': 'Dados JSON inválidos'}), 400
                
            app.logger.info(f"Dados recebidos: {list(data.keys()) if data else 'None'}")
            
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                app.logger.warning(f"Campos obrigatórios ausentes - Email: {bool(email)}, Password: {bool(password)}")
                return jsonify({'message': 'Email e senha são obrigatórios'}), 400

            app.logger.info(f"Tentativa de login para email: {email}")
            
            # Buscar usuário no banco
            try:
                from models.user import User
                user = User.query.filter_by(email=email).first()
                app.logger.info(f"Usuário encontrado: {bool(user)}")
            except Exception as db_error:
                app.logger.error(f"Erro ao buscar usuário no banco: {str(db_error)}")
                return jsonify({'message': 'Erro interno no servidor - banco de dados'}), 500

            if not user:
                app.logger.warning(f"Usuário não encontrado: {email}")
                return jsonify({'message': 'Email ou senha inválidos'}), 401
                
            # Verificar senha
            try:
                password_valid = user.check_password(password)
                app.logger.info(f"Senha válida: {password_valid}")
            except Exception as pwd_error:
                app.logger.error(f"Erro ao verificar senha: {str(pwd_error)}")
                return jsonify({'message': 'Erro interno no servidor - autenticação'}), 500
                
            if not password_valid:
                app.logger.warning(f"Senha inválida para usuário: {email}")
                return jsonify({'message': 'Email ou senha inválidos'}), 401

            if not user.is_active:
                app.logger.warning(f"Usuário inativo: {email}")
                return jsonify({'message': 'Conta desativada. Entre em contato com o suporte.'}), 403

            app.logger.info("Credenciais validadas com sucesso")
            
            # Preparar resposta simplificada (sem sessões complexas)
            response_data = {
                'message': 'Login realizado com sucesso',
                'status': 'success',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_admin': user.is_admin,
                    'is_active': user.is_active
                }
            }
            
            app.logger.info("=== LOGIN SIMPLIFICADO CONCLUÍDO COM SUCESSO ===")
            return jsonify(response_data), 200
            
        except Exception as e:
            app.logger.error("=== ERRO CRÍTICO NO LOGIN SIMPLIFICADO ===")
            app.logger.error(f"Tipo do erro: {type(e).__name__}")
            app.logger.error(f"Mensagem: {str(e)}")
            
            # Log do traceback completo
            import traceback
            app.logger.error(f"Traceback: {traceback.format_exc()}")
            
            try:
                db.session.rollback()
            except:
                pass
                
            return jsonify({
                'message': 'Erro interno no servidor',
                'error_type': type(e).__name__,
                'debug_info': str(e) if app.debug else None
            }), 500

    # --- Dashboard Endpoints ---
    @app.route('/api/dashboard/stats', methods=['GET'])
    def get_dashboard_stats():
        """Retorna estatísticas do dashboard"""
        try:
            app.logger.info("=== DASHBOARD STATS ===")
            
            # Dados simulados para evitar erros 404
            stats_data = {
                'success': True,
                'data': {
                    'total_trades': 0,
                    'open_positions': 0,
                    'total_profit': 0,
                    'win_rate': 0,
                    'account_balance': 0
                },
                'message': 'Estatísticas carregadas com sucesso'
            }
            
            return jsonify(stats_data), 200
            
        except Exception as e:
            app.logger.error(f"Erro ao buscar estatísticas: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno no servidor',
                'error': str(e)
            }), 500

    @app.route('/api/dashboard/account-balance', methods=['GET'])
    def get_account_balance():
        """Retorna saldo da conta"""
        try:
            app.logger.info("=== ACCOUNT BALANCE ===")
            
            # Dados simulados para evitar erros 404
            balance_data = {
                'success': True,
                'available_balance': 0,
                'total_balance': 0,
                'unrealized_pnl': 0,
                'margin_ratio': 0,
                'currency': 'USDT',
                'api_configured': False,
                'message': 'Configure suas credenciais da API Bitget no perfil'
            }
            
            return jsonify(balance_data), 200
            
        except Exception as e:
            app.logger.error(f"Erro ao buscar saldo: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno no servidor',
                'error': str(e)
            }), 500

    @app.route('/api/dashboard/open-positions', methods=['GET'])
    def get_open_positions():
        """Retorna posições abertas"""
        try:
            app.logger.info("=== OPEN POSITIONS ===")
            
            # Dados simulados para evitar erros 404
            positions_data = {
                'success': True,
                'data': [],
                'message': 'Configure suas credenciais da API Bitget no perfil para ver posições reais'
            }
            
            return jsonify(positions_data), 200
            
        except Exception as e:
            app.logger.error(f"Erro ao buscar posições: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Erro interno no servidor',
                'error': str(e)
            }), 500

    # --- Rota Raiz ---
    @app.route('/')
    def home():
        """Página inicial da API BigWhale"""
        return jsonify({
            "message": "🐋 BigWhale API - Sistema de Trading",
            "version": "1.0.0",
            "status": "online",
            "endpoints": {
                "login": "/api/auth/login",
                "session": "/api/auth/session",
                "health": "/api/health",
                "test": "/api/test",
                "dashboard_stats": "/api/dashboard/stats",
                "account_balance": "/api/dashboard/account-balance",
                "open_positions": "/api/dashboard/open-positions"
            },
            "documentation": "API para sistema de trading de criptomoedas",
            "environment": "development"
        }), 200

    # --- Endpoint de Sessão ---
    @app.route('/api/auth/session', methods=['GET'])
    def check_session():
        """Verifica se há uma sessão ativa (versão simplificada)"""
        try:
            app.logger.info("=== VERIFICAÇÃO DE SESSÃO ===")
            
            # Por enquanto, retorna que não há sessão ativa
            # Em uma implementação completa, verificaria cookies/tokens
            response_data = {
                'authenticated': False,
                'message': 'Nenhuma sessão ativa encontrada'
            }
            
            app.logger.info("Verificação de sessão concluída")
            return jsonify(response_data), 200
            
        except Exception as e:
            app.logger.error(f"Erro na verificação de sessão: {str(e)}")
            return jsonify({
                'authenticated': False,
                'error': 'Erro interno no servidor'
            }), 500

    # --- Rota de Teste Simples ---
    @app.route('/api/test')
    def test_route():
        return jsonify({"message": "Backend BigWhale funcionando no Render!", "environment": "Render"}), 200

    # --- Rota de Health Check ---
    @app.route('/api/health')
    def health_check():
        """Endpoint para verificar a saúde da aplicação"""
        try:
            app.logger.info("=== HEALTH CHECK INICIADO ===")
            
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'environment': 'Render',
                'message': 'Sistema BigWhale funcionando corretamente no Render'
            }
            
            # Verificar conexão com banco
            try:
                from models.user import User
                user_count = User.query.count()
                health_data['database'] = 'connected'
                health_data['users_count'] = user_count
                app.logger.info(f"Banco de dados conectado - {user_count} usuários")
            except Exception as db_error:
                app.logger.error(f"Erro no banco de dados: {str(db_error)}")
                health_data['database'] = 'error'
                health_data['database_error'] = str(db_error)
            
            app.logger.info("=== HEALTH CHECK CONCLUÍDO ===")
            return jsonify(health_data), 200
            
        except Exception as e:
            app.logger.error(f"=== HEALTH CHECK FALHOU ===")
            app.logger.error(f"Erro: {str(e)}")
            
            import traceback
            app.logger.error(f"Traceback: {traceback.format_exc()}")
            
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    # --- Criação do Banco de Dados ---
    with app.app_context():
        try:
            db.create_all()
            print(f"✅ Tabelas do banco de dados SQLite verificadas/criadas com sucesso!")
            # Garantir credenciais de admin
            ensure_admin_credentials()
        except Exception as e:
            print(f"❌ Erro ao criar tabelas SQLite: {e}")

    return app

# Criar a aplicação para o Render
application = create_app()

if __name__ == '__main__':
    # Para desenvolvimento local
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Iniciando servidor...")
    print(f"🌐 Porta: {port}")
    print("🔧 Ambiente: Desenvolvimento")
    print("📧 Credenciais disponíveis:")
    print("   admin@bigwhale.com / Raikamaster1@")
    print("   willian@lexxusadm.com.br / Bigwhale202021@ (ADMIN)")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )