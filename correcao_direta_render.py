#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correção direta para o ambiente Render
Este script deve ser executado diretamente no ambiente do Render
"""

import os
import sys
import logging
import subprocess
import importlib.util
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def instalar_psycopg2():
    """Instala o pacote psycopg2-binary"""
    try:
        logger.info("Instalando psycopg2-binary...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
        logger.info("✅ psycopg2-binary instalado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao instalar psycopg2-binary: {e}")
        return False

def criar_tabela_active_signals():
    """Cria a tabela active_signals diretamente"""
    try:
        logger.info("Criando tabela active_signals...")
        
        # Importar dependências necessárias
        from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        
        # Definir o caminho do banco SQLite no Render
        if os.environ.get('RENDER'):
            db_path = '/tmp/site.db'
        else:
            db_path = os.path.join(os.getcwd(), 'instance', 'site.db')
        
        # Criar engine e sessão
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        Base = declarative_base()
        
        # Definir modelo ActiveSignal
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
        
        # Criar tabela
        Base.metadata.create_all(engine)
        
        # Verificar se a tabela foi criada
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'active_signals' in tables:
            logger.info("✅ Tabela active_signals criada com sucesso!")
            
            # Mostrar colunas
            columns = [col['name'] for col in inspector.get_columns('active_signals')]
            logger.info(f"Colunas: {columns}")
            
            return True
        else:
            logger.error("❌ Falha ao criar tabela active_signals!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela active_signals: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def corrigir_rotas_app():
    """Corrige problemas de roteamento na aplicação"""
    try:
        logger.info("Corrigindo rotas da aplicação...")
        
        # Verificar se app_corrigido.py existe
        if not os.path.exists('app_corrigido.py'):
            logger.error("❌ Arquivo app_corrigido.py não encontrado!")
            return False
        
        # Ler conteúdo do arquivo
        with open('app_corrigido.py', 'r') as f:
            conteudo = f.read()
        
        # Verificar se já existe rota raiz
        if "def home():" not in conteudo and "@app.route('/')" not in conteudo:
            logger.info("Adicionando rota raiz (/)...")
            
            # Encontrar posição para inserir a rota
            posicao = conteudo.find("# --- Rota de Teste Simples ---")
            if posicao == -1:
                posicao = conteudo.find("@app.route('/api/test')")
            
            if posicao != -1:
                # Inserir rota raiz
                nova_rota = """
    # --- Rota Raiz ---
    @app.route('/')
    def home():
        return jsonify({"message": "BigWhale Backend API", "status": "running"}), 200
                
"""
                novo_conteudo = conteudo[:posicao] + nova_rota + conteudo[posicao:]
                
                # Salvar arquivo modificado
                with open('app_corrigido.py', 'w') as f:
                    f.write(novo_conteudo)
                
                logger.info("✅ Rota raiz (/) adicionada com sucesso!")
            else:
                logger.warning("⚠️ Não foi possível encontrar local para inserir rota raiz")
        else:
            logger.info("✅ Rota raiz (/) já existe!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir rotas: {e}")
        return False

def corrigir_auto_monitor():
    """Corrige o serviço de monitoramento automático"""
    try:
        logger.info("Corrigindo serviço de monitoramento automático...")
        
        # Verificar se o arquivo existe
        if not os.path.exists('backend/services/auto_monitor_service.py'):
            logger.error("❌ Arquivo auto_monitor_service.py não encontrado!")
            return False
        
        # Ler conteúdo do arquivo
        with open('backend/services/auto_monitor_service.py', 'r') as f:
            conteudo = f.read()
        
        # Adicionar tratamento de erro para tabela inexistente
        if "except Exception as db_error:" in conteudo and "self.logger.error(f\"Erro ao buscar sinais do banco: {db_error}\")" in conteudo:
            # Já tem tratamento de erro, vamos melhorar
            novo_conteudo = conteudo.replace(
                "self.logger.error(f\"Erro ao buscar sinais do banco: {db_error}\")",
                "self.logger.error(f\"Erro ao buscar sinais do banco: {db_error}\")\n                # Tentar criar a tabela se não existir\n                try:\n                    with self.app.app_context():\n                        db.create_all()\n                        self.logger.info(\"Tentativa de criar tabelas ausentes\")\n                except Exception as create_error:\n                    self.logger.error(f\"Erro ao criar tabelas: {create_error}\")"
            )
            
            # Salvar arquivo modificado
            with open('backend/services/auto_monitor_service.py', 'w') as f:
                f.write(novo_conteudo)
            
            logger.info("✅ Serviço de monitoramento corrigido!")
        else:
            logger.warning("⚠️ Não foi possível encontrar local para corrigir o serviço de monitoramento")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir serviço de monitoramento: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=== INICIANDO CORREÇÃO DIRETA NO RENDER ===")
    
    # Instalar psycopg2
    instalar_psycopg2()
    
    # Criar tabela active_signals
    criar_tabela_active_signals()
    
    # Corrigir rotas
    corrigir_rotas_app()
    
    # Corrigir serviço de monitoramento
    corrigir_auto_monitor()
    
    logger.info("=== CORREÇÃO DIRETA CONCLUÍDA ===")
    logger.info("Reinicie a aplicação no Render para aplicar as correções")

if __name__ == "__main__":
    main()