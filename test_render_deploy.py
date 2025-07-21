#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o deploy no Render
Verifica se todas as correções foram aplicadas
"""

import os
import sys
import logging
import importlib.util
import requests

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

def check_database_tables():
    """Verifica se as tabelas necessárias existem no banco de dados"""
    try:
        logger.info("Verificando tabelas do banco de dados...")
        
        # Importar dependências
        from database import db
        from app import create_app
        
        # Criar aplicação e contexto
        app = create_app()
        with app.app_context():
            # Verificar tabelas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Verificar tabelas críticas
            critical_tables = ['users', 'active_signals']
            missing_tables = [table for table in critical_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"❌ Tabelas faltando: {missing_tables}")
                return False
            else:
                logger.info(f"✅ Todas as tabelas críticas existem: {critical_tables}")
                return True
                
    except Exception as e:
        logger.error(f"❌ Erro ao verificar tabelas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_api_endpoints(base_url=None):
    """Verifica se os endpoints da API estão funcionando"""
    try:
        logger.info("Verificando endpoints da API...")
        
        # Se não for fornecido um URL base, usar localhost
        if not base_url:
            base_url = "http://localhost:5000"
        
        # Verificar endpoint de health check
        health_url = f"{base_url}/api/health"
        logger.info(f"Verificando endpoint: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Endpoint de health check funcionando: {response.status_code}")
            return True
        else:
            logger.error(f"❌ Erro no endpoint de health check: {response.status_code}")
            return False
                
    except Exception as e:
        logger.error(f"❌ Erro ao verificar endpoints: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=== INICIANDO TESTE DE DEPLOY NO RENDER ===")
    
    # Verificar se psycopg2 está instalado
    if check_module_installed('psycopg2'):
        logger.info("✅ psycopg2 está instalado")
    else:
        logger.error("❌ psycopg2 não está instalado")
    
    # Verificar tabelas do banco de dados
    check_database_tables()
    
    # Verificar endpoints da API (apenas se for fornecido um URL)
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        check_api_endpoints(base_url)
    else:
        logger.info("Nenhum URL fornecido, pulando verificação de endpoints")
    
    logger.info("=== TESTE DE DEPLOY CONCLUÍDO ===")

if __name__ == "__main__":
    main()