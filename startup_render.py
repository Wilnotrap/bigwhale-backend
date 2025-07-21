#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização automática para o Render
Este script é executado automaticamente quando a aplicação inicia
"""

import os
import sys
import logging
import subprocess
import importlib.util

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def instalar_dependencias():
    """Instala dependências necessárias"""
    try:
        # Verificar se psycopg2 está instalado
        try:
            import psycopg2
            logger.info("✅ psycopg2 já está instalado")
        except ImportError:
            logger.info("Instalando psycopg2-binary...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
            logger.info("✅ psycopg2-binary instalado com sucesso!")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao instalar dependências: {e}")
        return False

def criar_tabelas_necessarias():
    """Cria todas as tabelas necessárias"""
    try:
        logger.info("Criando tabelas necessárias...")
        
        # Importar dependências
        from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
        from sqlalchemy.ext.declarative import declarative_base
        from datetime import datetime
        
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
        
        # Definir todos os modelos necessários
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
        
        # Verificar se as tabelas foram criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"✅ Tabelas criadas: {tables}")
        
        # Verificar tabelas críticas
        critical_tables = ['users', 'active_signals', 'user_sessions', 'trades']
        missing_tables = [table for table in critical_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"❌ Tabelas faltando: {missing_tables}")
            return False
        else:
            logger.info("✅ Todas as tabelas críticas foram criadas com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def criar_usuario_demo():
    """Cria usuário demo se não existir"""
    try:
        logger.info("Verificando usuário demo...")
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from werkzeug.security import generate_password_hash
        
        # Definir o caminho do banco SQLite no Render
        if os.environ.get('RENDER'):
            db_path = '/tmp/site.db'
        else:
            db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
        
        # Criar engine e sessão
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar se usuário demo existe
        result = session.execute("SELECT COUNT(*) FROM users WHERE email = 'financeiro@lexxusadm.com.br'").fetchone()
        
        if result[0] == 0:
            # Criar usuário demo
            password_hash = generate_password_hash('FinanceiroDemo2025@')
            session.execute("""
                INSERT INTO users (full_name, email, password_hash, is_active, is_admin, operational_balance_usd)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('Conta Demo Financeiro', 'financeiro@lexxusadm.com.br', password_hash, True, False, 600.0))
            
            session.commit()
            logger.info("✅ Usuário demo criado com sucesso!")
        else:
            logger.info("✅ Usuário demo já existe!")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar usuário demo: {e}")
        return False

def main():
    """Função principal de inicialização"""
    logger.info("=== INICIANDO CONFIGURAÇÃO AUTOMÁTICA DO RENDER ===")
    
    # Instalar dependências
    instalar_dependencias()
    
    # Criar tabelas
    criar_tabelas_necessarias()
    
    # Criar usuário demo
    criar_usuario_demo()
    
    logger.info("=== CONFIGURAÇÃO AUTOMÁTICA CONCLUÍDA ===")
    logger.info("Aplicação pronta para uso!")

if __name__ == "__main__":
    main()