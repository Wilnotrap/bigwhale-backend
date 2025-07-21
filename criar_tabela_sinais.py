#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar a tabela active_signals no banco de dados
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def criar_tabela_sinais():
    """Cria a tabela active_signals no banco de dados"""
    try:
        logger.info("=== INICIANDO CRIAÇÃO DA TABELA ACTIVE_SIGNALS ===")
        
        # Importar dependências
        from database import db
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
            
            # Importar modelo
            from models.active_signal import ActiveSignal
            
            # Criar tabela
            logger.info("Criando tabela active_signals...")
            db.create_all()
            
            # Verificar novamente
            tables = inspector.get_table_names()
            if 'active_signals' in tables:
                logger.info("✅ Tabela active_signals criada com sucesso!")
                
                # Verificar estrutura da tabela
                columns = inspector.get_columns('active_signals')
                column_names = [col['name'] for col in columns]
                logger.info(f"Colunas criadas: {column_names}")
                
                return True
            else:
                logger.error("❌ Falha ao criar tabela active_signals!")
                return False
                
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela active_signals: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = criar_tabela_sinais()
    
    if success:
        logger.info("✅ Tabela active_signals criada com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Erro ao criar tabela active_signals!")
        sys.exit(1)