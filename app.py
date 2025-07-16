#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Flask Final - Sistema Bitget
Versão corrigida e funcional para deploy no Render.com
"""

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta, datetime
import logging
from logging.handlers import RotatingFileHandler

# Carregar variáveis de ambiente
load_dotenv()

def configure_python_path():
    """Configura PYTHONPATH para encontrar módulos corretamente"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Adicionar diretório backend ao path
    backend_path = os.path.join(current_dir, 'backend')
    if os.path.exists(backend_path) and backend_path not in sys.path:
        sys.path.insert(0, backend_path)
        print(f"✅ Backend path adicionado: {backend_path}")
    
    # Adicionar diretório raiz ao path
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        print(f"✅ Root path adicionado: {current_dir}")

def import_modules_safely():
    """Importa módulos com fallbacks seguros"""
    modules = {}
    
    try:
        # Importar database
        try:
            from backend.database import db
            modules['db'] = db
            print("✅ Database importado (backend)")
        except ImportError:
            try:
                from database import db
                modules['db'] = db
                print("✅ Database importado (root)")
            except ImportError:
                print("⚠️ Database não disponível")
                modules['db'] = None
        
        # Importar User model
        try:
            from backend.models.user import User
            modules['User'] = User
            print("✅ User model importado (backend)")
        except ImportError:
            try:
                from models.user import User
                modules['User'] = User
                print("✅ User model importado (root)")
            except ImportError:
                print("⚠️ User model não disponível")
                modules['User'] = None
        
        # Importar blueprints se disponíveis
        blueprints_imported = 0
        
        # Auth blueprint
        try:
            from backend.auth.routes import auth_bp
            modules['auth_bp'] = auth_bp
            blueprints_imported += 1
            print("✅ Auth blueprint importado")
        except ImportError:
            print("⚠️ Auth blueprint não disponível")
            modules['auth_bp'] = None
        
        # Dashboard blueprint
        try:
            from backend.api.dashboard import dashboard_bp
            modules['dashboard_bp'] = dashboard_bp
            blueprints_imported += 1
            print("✅ Dashboard blueprint importado")
        except ImportError:
            print("⚠️ Dashboard blueprint não disponível")
            modules['dashboard_bp'] = None
        
        # Admin blueprint
        try:
            from backend.api.admin import admin_bp
            modules['admin_bp'] = admin_bp
            blueprints_imported += 1
            print("✅ Admin blueprint importado")
        except ImportError:
            print("⚠️ Admin blueprint não disponível")
            modules['admin_bp'] = None
        
        # Stripe webhook
        try:
            from backend.api.stripe_webhook import stripe_webhook_bp
            modules['stripe_webhook_bp'] = stripe_webhook_bp
            blueprints_imported += 1
            print("✅ Stripe webhook importado")
        except ImportError:
            print("⚠️ Stripe webhook não disponível")
            modules['stripe_webhook_bp'] = None
        
        # API credentials
        try:
            from backend.api import api_credentials_bp
            modules['api_credentials_bp'] = api_credentials_bp
            blueprints_imported += 1
            print("✅ API credentials importado")
        except ImportError:
            print("⚠️ API credentials não disponível")
            modules['api_credentials_bp'] = None
        
        # Auth middleware
        try:
            from backend.middleware.auth_middleware import AuthMiddleware
            modules['AuthMiddleware'] = AuthMiddleware
            print("✅ Auth middleware importado")
        except ImportError:
            print("⚠️ Auth middleware não disponível")
            modules['AuthMiddleware'] = None
        
        # Admin credentials function
        try:
            from backend.auth.login import ensure_admin_credentials
            modules['ensure_admin_credentials'] = ensure_admin_credentials
            print("✅ Admin credentials function importada")
        except ImportError:
            print("⚠️ Admin credentials function não disponível")
            modules['ensure_admin_credentials'] = None
        
        print(f"✅ Importações concluídas: {blueprints_imported} blueprints disponíveis")
        return modules
        
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        return {'db': None, 'User': None}

def create_simple_admin_user(db, User):
    """Cria usuário admin simples se não existir"""
    try:
        if User is None or db is None:
            print("⚠️ User model ou DB não disponível, pulando criação de admin")
            return
        
        admin_user = User.query.filter_by(email='admin@bigwhale.com').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                full_name='Admin BigWhale',
                email='admin@bigwhale.com',
                password_hash=generate_password_hash('Raikamaster1@'),
                is_active=True,
                is_admin=True
            )
            db.session.add(admin_user)
            
            # Segundo admin
            admin_user2 = User(
                full_name='Willian Admin',
                email='willian@lexxusadm.com.br',
                password_hash=generate_password_hash('Bigwhale202021@'),
                is_active=True,
                is_admin=True
            )
            db.session.add(admin_user2)
            
            db.session.commit()
            print("✅ Usuários admin criados")
        else:
            print("✅ Usuários admin já existem")
            
    except Exception as e:
        print(f"⚠️ Erro ao criar usuários admin: {e}")
        try:
            if db:
                db.session.rollback()
        except:
            pass

def create_app():
    """Cria e configura a aplicação Flask"""
    
    # Configurar paths antes de qualquer importação
    configure_python_path()
    
    # Importar módulos com fallbacks
    modules = import_modules_safely()
    
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuração de Logging
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
    
    # Configuração da Aplicação
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'),
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=2592000,  # 30 dias
        AES_ENCRYPTION_KEY=os.environ.get('AES_ENCRYPTION_KEY', 'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789')
    )
    
    # Configuração do Banco de Dados
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and os.environ.get('RENDER'):
        # PostgreSQL em produção no Render
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print("✅ Conectando ao PostgreSQL em produção")
    else:
        # SQLite para desenvolvimento
        if os.environ.get('RENDER'):
            db_path = '/tmp/site.db'
        else:
            instance_path = app.instance_path
            if not os.path.exists(instance_path):
                os.makedirs(instance_path)
            db_path = os.path.join(instance_path, 'site.db')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        print(f"✅ Conectando ao SQLite: {db_path}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração CORS CORRIGIDA
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
             "http://bwhale.site",
             "https://bigwhale-backend.onrender.com"
         ],
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         expose_headers=["Content-Type", "Authorization"])
    
    # Inicializar extensões
    if modules.get('db'):
        modules['db'].init_app(app)
        print("✅ Database inicializado")
    
    # Configurar Flask-Session
    try:
        from flask_session import Session
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_PERMANENT'] = True
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_KEY_PREFIX'] = 'bigwhale:'
        app.config['SESSION_FILE_DIR'] = os.path.join(app.instance_path, 'flask_session')
        app.config['SESSION_FILE_THRESHOLD'] = 500
        app.config['SESSION_FILE_MODE'] = 384
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
        
        session_dir = app.config['SESSION_FILE_DIR']
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
            app.logger.info(f"Diretório de sessão criado: {session_dir}")
        
        Session(app)
        app.logger.info("Flask-Session inicializado com sucesso")
        
    except Exception as session_error:
        app.logger.error(f"Erro ao configurar Flask-Session: {str(session_error)}")
        app.config['SESSION_TYPE'] = 'null'

    # Inicializar banco de dados
    if modules.get('db'):
        with app.app_context():
            try:
                modules['db'].create_all()
                app.logger.info("Tabelas do banco de dados garantidas na inicialização")
                
                # Criar usuários admin
                create_simple_admin_user(modules['db'], modules.get('User'))
                
                # Chamar função de admin credentials se disponível
                if modules.get('ensure_admin_credentials'):
                    try:
                        modules['ensure_admin_credentials']()
                    except Exception as e:
                        app.logger.warning(f"Erro ao executar ensure_admin_credentials: {e}")
            except Exception as db_error:
                app.logger.error(f"Erro ao inicializar banco: {db_error}")

    # Registrar Blueprints disponíveis
    blueprints_registered = 0
    
    if modules.get('auth_bp'):
        app.register_blueprint(modules['auth_bp'], url_prefix='/api/auth')
        blueprints_registered += 1
        
    if modules.get('dashboard_bp'):
        app.register_blueprint(modules['dashboard_bp'], url_prefix='/api/dashboard')
        blueprints_registered += 1
        
    if modules.get('admin_bp'):
        app.register_blueprint(modules['admin_bp'], url_prefix='/api/admin')
        blueprints_registered += 1
        
    if modules.get('stripe_webhook_bp'):
        app.register_blueprint(modules['stripe_webhook_bp'], url_prefix='/api')
        blueprints_registered += 1
        
    if modules.get('api_credentials_bp'):
        app.register_blueprint(modules['api_credentials_bp'], url_prefix='/api')
        blueprints_registered += 1
    
    print(f"✅ {blueprints_registered} blueprints registrados")

    # Middleware de autenticação
    if modules.get('AuthMiddleware'):
        modules['AuthMiddleware'](app)
        print("✅ Auth middleware configurado")

    # ROTAS ESSENCIAIS
    @app.route('/')
    def home():
        return jsonify({
            "message": "🐋 Backend BigWhale Online!",
            "status": "running",
            "environment": "Render" if os.environ.get('RENDER') else "Local",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0"
        })

    @app.route('/api/health')
    def health_check():
        """Health check com diagnóstico completo"""
        try:
            health_data = {
                "status": "healthy",
                "message": "Backend BigWhale funcionando!",
                "environment": "Render" if os.environ.get('RENDER') else "Development",
                "timestamp": datetime.now().isoformat(),
                "modules_loaded": len([k for k, v in modules.items() if v is not None]),
                "blueprints_registered": blueprints_registered,
                "version": "3.0.0"
            }
            
            # Verificar conexão com banco
            if modules.get('db') and modules.get('User'):
                try:
                    user_count = modules['User'].query.count()
                    health_data['database'] = {
                        'status': 'connected',
                        'users_count': user_count,
                        'connection_test': 'passed'
                    }
                except Exception as db_error:
                    health_data['database'] = {
                        'status': 'error',
                        'error': str(db_error),
                        'connection_test': 'failed'
                    }
                    health_data['status'] = 'degraded'
            else:
                health_data['database'] = {
                    'status': 'not_available',
                    'reason': 'Database or User model not loaded'
                }
            
            # Verificar blueprints registrados
            registered_blueprints = [bp.name for bp in app.blueprints.values()]
            health_data['blueprints'] = {
                'registered': registered_blueprints,
                'count': len(registered_blueprints)
            }
            
            return jsonify(health_data), 200
            
        except Exception as e:
            import traceback
            return jsonify({
                "status": "unhealthy",
                "message": "Erro crítico na verificação de saúde",
                "error": str(e),
                "traceback": traceback.format_exc()[:1000],
                "timestamp": datetime.now().isoformat()
            }), 503

    @app.route('/api/test')
    def test_route():
        return jsonify({
            "message": "🚀 API BigWhale funcionando no Render!",
            "environment": "Render" if os.environ.get('RENDER') else "Development",
            "modules_available": [k for k, v in modules.items() if v is not None],
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "cors_fixed": True
        }), 200

    @app.route('/api/debug/modules')
    def debug_modules():
        """Debug de módulos carregados"""
        return jsonify({
            "modules": {k: str(type(v)) for k, v in modules.items()},
            "python_path": sys.path[:5],
            "current_dir": os.getcwd(),
            "environment": {
                "RENDER": os.environ.get('RENDER'),
                "DATABASE_URL": bool(os.environ.get('DATABASE_URL'))
            }
        }), 200

    # Login básico se User model estiver disponível
    if modules.get('User') and modules.get('db'):
        @app.route('/api/auth/login', methods=['POST'])
        def login():
            """Endpoint básico de login"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'Dados não fornecidos'}), 400
                    
                email = data.get('email')
                password = data.get('password')
                
                if not email or not password:
                    return jsonify({'error': 'Email e senha são obrigatórios'}), 400
                
                user = modules['User'].query.filter_by(email=email).first()
                if user and user.check_password(password) and user.is_active:
                    return jsonify({
                        'success': True,
                        'message': 'Login realizado com sucesso',
                        'user': {
                            'id': user.id,
                            'email': user.email,
                            'full_name': user.full_name,
                            'is_admin': user.is_admin
                        }
                    }), 200
                else:
                    return jsonify({'error': 'Credenciais inválidas'}), 401
                    
            except Exception as e:
                app.logger.error(f"Erro no login: {e}")
                return jsonify({'error': 'Erro interno do servidor'}), 500

    # Tratamento de erros
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint não encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erro interno do servidor'}), 500

    return app

# Criar aplicação para o Render
application = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Iniciando Backend BigWhale...")
    print(f"🌐 Porta: {port}")
    print(f"🔧 Ambiente: {'Render' if os.environ.get('RENDER') else 'Development'}")
    print("📧 Credenciais disponíveis:")
    print("   admin@bigwhale.com / Raikamaster1@")
    print("   willian@lexxusadm.com.br / Bigwhale202021@")
    
    application.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )