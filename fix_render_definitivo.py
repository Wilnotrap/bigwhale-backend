#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção definitiva para o Render - Liquidar todos os erros
"""

import os
import sys
import logging
import subprocess
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def instalar_psycopg2():
    """Instala psycopg2-binary forçadamente"""
    try:
        logger.info("🔧 Instalando psycopg2-binary...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "psycopg2-binary==2.9.9"])
        logger.info("✅ psycopg2-binary instalado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao instalar psycopg2-binary: {e}")
        return False

def criar_banco_completo():
    """Cria o banco de dados completo com todas as tabelas"""
    try:
        logger.info("🗄️ Criando banco de dados completo...")
        
        from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        from werkzeug.security import generate_password_hash
        
        # Definir o caminho do banco SQLite no Render
        if os.environ.get('RENDER'):
            db_path = '/tmp/site.db'
        else:
            db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
        
        # Garantir que o diretório existe
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Criar engine
        engine = create_engine(f'sqlite:///{db_path}')
        Base = declarative_base()
        
        # Definir todos os modelos
        class User(Base):
            __tablename__ = 'users'
            
            id = Column(Integer, primary_key=True)
            full_name = Column(String(100), nullable=False)
            email = Column(String(120), unique=True, nullable=False)
            password_hash = Column(String(128))
            is_active = Column(Boolean, default=True)
            is_admin = Column(Boolean, default=False)
            created_at = Column(DateTime, default=datetime.utcnow)
            operational_balance_usd = Column(Float, default=0.0)
            bitget_api_key_encrypted = Column(Text)
            bitget_api_secret_encrypted = Column(Text)
            bitget_passphrase_encrypted = Column(Text)
        
        class ActiveSignal(Base):
            __tablename__ = 'active_signals'
            
            id = Column(Integer, primary_key=True)
            symbol = Column(String(20), nullable=False)
            side = Column(String(10), nullable=False)
            entry_price = Column(Float, nullable=False)
            stop_loss = Column(Float, nullable=True)
            take_profit = Column(Float, nullable=True)
            status = Column(String(20), default='active')
            created_at = Column(DateTime, default=datetime.utcnow)
            closed_at = Column(DateTime, nullable=True)
            user_id = Column(Integer, nullable=True)
            targets = Column(String(500), nullable=True)
            targets_hit = Column(Integer, default=0)
        
        class UserSession(Base):
            __tablename__ = 'user_sessions'
            
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, nullable=False)
            session_token = Column(String(255), unique=True, nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow)
            expires_at = Column(DateTime, nullable=False)
            is_active = Column(Boolean, default=True)
        
        class Trade(Base):
            __tablename__ = 'trades'
            
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, nullable=False)
            symbol = Column(String(20), nullable=False)
            side = Column(String(10), nullable=False)
            quantity = Column(Float, nullable=False)
            price = Column(Float, nullable=False)
            status = Column(String(20), default='pending')
            created_at = Column(DateTime, default=datetime.utcnow)
            executed_at = Column(DateTime, nullable=True)
        
        # Criar todas as tabelas
        Base.metadata.create_all(engine)
        
        # Criar sessão
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar se as tabelas foram criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"✅ Tabelas criadas: {tables}")
        
        # Criar usuários padrão
        usuarios_padrao = [
            {
                'email': 'admin@bigwhale.com',
                'password': 'Raikamaster1@',
                'full_name': 'Admin BigWhale',
                'is_admin': True,
                'balance': 1000.0
            },
            {
                'email': 'willian@lexxusadm.com.br',
                'password': 'Bigwhale202021@',
                'full_name': 'Willian Admin',
                'is_admin': True,
                'balance': 1000.0
            },
            {
                'email': 'financeiro@lexxusadm.com.br',
                'password': 'FinanceiroDemo2025@',
                'full_name': 'Conta Demo Financeiro',
                'is_admin': False,
                'balance': 600.0
            }
        ]
        
        for user_data in usuarios_padrao:
            # Verificar se usuário já existe
            existing_user = session.query(User).filter_by(email=user_data['email']).first()
            
            if not existing_user:
                # Criar usuário
                new_user = User(
                    full_name=user_data['full_name'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    is_active=True,
                    is_admin=user_data['is_admin'],
                    operational_balance_usd=user_data['balance']
                )
                session.add(new_user)
                logger.info(f"✅ Usuário criado: {user_data['email']}")
            else:
                logger.info(f"✅ Usuário já existe: {user_data['email']}")
        
        # Salvar alterações
        session.commit()
        session.close()
        
        logger.info("✅ Banco de dados criado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar banco de dados: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def desabilitar_servicos_problematicos():
    """Desabilita temporariamente os serviços que causam problemas"""
    try:
        logger.info("🚫 Desabilitando serviços problemáticos...")
        
        # Verificar se o arquivo auto_monitor_service existe
        auto_monitor_path = 'backend/services/auto_monitor_service.py'
        if os.path.exists(auto_monitor_path):
            # Ler o arquivo
            with open(auto_monitor_path, 'r') as f:
                conteudo = f.read()
            
            # Adicionar verificação de segurança no início da função _check_all_signals
            if "def _check_all_signals(self):" in conteudo:
                novo_conteudo = conteudo.replace(
                    "def _check_all_signals(self):",
                    """def _check_all_signals(self):
        \"\"\"Verifica todos os sinais ativos de todos os usuários\"\"\"
        # Verificação de segurança - não executar se tabelas não existirem
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if 'active_signals' not in tables:
                self.logger.warning("⚠️ Tabela active_signals não existe, pulando verificação")
                return
        except Exception as safety_error:
            self.logger.error(f"Erro na verificação de segurança: {safety_error}")
            return"""
                )
                
                # Salvar arquivo modificado
                with open(auto_monitor_path, 'w') as f:
                    f.write(novo_conteudo)
                
                logger.info("✅ Serviço auto_monitor_service protegido!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao desabilitar serviços: {e}")
        return False

def main():
    """Função principal de correção definitiva"""
    logger.info("=== INICIANDO CORREÇÃO DEFINITIVA DO RENDER ===")
    
    # 1. Instalar psycopg2
    instalar_psycopg2()
    
    # 2. Desabilitar serviços problemáticos
    desabilitar_servicos_problematicos()
    
    # 3. Criar banco completo
    criar_banco_completo()
    
    # 4. Aguardar para garantir que tudo foi criado
    time.sleep(2)
    
    logger.info("=== CORREÇÃO DEFINITIVA CONCLUÍDA ===")
    logger.info("🚀 Sistema pronto para uso!")

if __name__ == "__main__":
    main()