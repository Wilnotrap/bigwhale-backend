#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir erros de deploy no Render
- Cria tabela active_signals se não existir
- Adiciona psycopg2-binary aos requirements se necessário
- Corrige erros de roteamento na aplicação
"""

import os
import sys
import logging
import importlib.util
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_module_installed(module_name):
    """Verifica se um módulo Python está instalado"""
    try:
        importlib.util.find_spec(module_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Instala um pacote Python usando pip"""
    try:
        logger.info(f"Instalando {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"✅ {package_name} instalado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao instalar {package_name}: {e}")
        return False

def create_active_signals_table():
    """Cria a tabela active_signals se não existir"""
    try:
        logger.info("Verificando tabela active_signals...")
        
        # Importar dependências
        from database import db
        from models.active_signal import ActiveSignal
        from app import create_app
        
        # Criar aplicação e contexto
        app = create_app()
        with app.app_context():
            # Verificar se a tabela existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'active_signals' in tables:
                logger.info("✅ Tabela active_signals já existe!")
                return True
            
            # Criar tabela
            logger.info("Criando tabela active_signals...")
            db.create_all()
            
            # Verificar novamente
            tables = inspector.get_table_names()
            if 'active_signals' in tables:
                logger.info("✅ Tabela active_signals criada com sucesso!")
                return True
            else:
                logger.error("❌ Falha ao criar tabela active_signals!")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela active_signals: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_requirements():
    """Verifica e atualiza requirements.txt se necessário"""
    try:
        logger.info("Verificando requirements.txt...")
        
        # Ler arquivo requirements.txt
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Verificar se psycopg2-binary está presente
        if 'psycopg2-binary' in requirements:
            logger.info("✅ psycopg2-binary já está em requirements.txt")
            return True
        
        # Adicionar psycopg2-binary
        logger.info("Adicionando psycopg2-binary a requirements.txt...")
        with open('requirements.txt', 'a') as f:
            f.write("\npsycopg2-binary==2.9.9\n")
        
        logger.info("✅ psycopg2-binary adicionado a requirements.txt")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar requirements.txt: {e}")
        return False

def fix_app_routing():
    """Corrige problemas de roteamento na aplicação"""
    try:
        logger.info("Verificando rotas da aplicação...")
        
        # Importar app
        from app import create_app
        
        # Criar aplicação e verificar rotas
        app = create_app()
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Verificar rota principal
        if '/' in routes:
            logger.info("✅ Rota principal (/) encontrada")
        else:
            logger.warning("⚠️ Rota principal (/) não encontrada")
            
            # Adicionar rota principal
            @app.route('/')
            def home():
                return "BigWhale Backend is running"
            
            logger.info("✅ Rota principal (/) adicionada")
        
        logger.info("✅ Verificação de rotas concluída")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar rotas: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=== INICIANDO CORREÇÃO DE ERROS DE DEPLOY ===")
    
    # Verificar se psycopg2 está instalado
    if not check_module_installed('psycopg2'):
        logger.info("psycopg2 não está instalado, instalando...")
        install_package('psycopg2-binary')
    else:
        logger.info("✅ psycopg2 já está instalado")
    
    # Verificar requirements.txt
    check_requirements()
    
    # Criar tabela active_signals
    create_active_signals_table()
    
    # Corrigir rotas
    fix_app_routing()
    
    logger.info("=== CORREÇÃO DE ERROS DE DEPLOY CONCLUÍDA ===")
    logger.info("Para aplicar as correções, reinicie a aplicação no Render")

if __name__ == "__main__":
    main()