#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para desativar serviços problemáticos
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def desativar_auto_monitor():
    """Desativa o serviço auto_monitor_service"""
    try:
        logger.info("Desativando serviço auto_monitor_service...")
        
        # Verificar se o arquivo existe
        if not os.path.exists('backend/services/auto_monitor_service.py'):
            logger.error("❌ Arquivo auto_monitor_service.py não encontrado!")
            return False
        
        # Fazer backup do arquivo
        if not os.path.exists('backend/services/auto_monitor_service.py.bak'):
            with open('backend/services/auto_monitor_service.py', 'r') as f:
                conteudo = f.read()
            
            with open('backend/services/auto_monitor_service.py.bak', 'w') as f:
                f.write(conteudo)
            
            logger.info("✅ Backup do serviço criado")
        
        # Criar versão simplificada do serviço
        conteudo_simples = """# backend/services/auto_monitor_service.py
import logging

logger = logging.getLogger(__name__)

class AutoMonitorService:
    """Versão simplificada do serviço de monitoramento"""
    
    def __init__(self, app):
        self.app = app
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔄 Serviço de monitoramento simplificado inicializado")
    
    def start(self):
        """Inicia o monitoramento (desativado)"""
        self.logger.info("⚠️ Monitoramento automático desativado")
    
    def stop(self):
        """Para o monitoramento (desativado)"""
        self.logger.info("⚠️ Monitoramento automático já está desativado")
    
    def force_check_all(self):
        """Força verificação (desativado)"""
        self.logger.info("⚠️ Verificação forçada desativada")
        return True

# Instância global do serviço
auto_monitor = None

def init_auto_monitor(app):
    """Inicializa o serviço de monitoramento (desativado)"""
    global auto_monitor
    logger.info("⚠️ Serviço auto_monitor desativado temporariamente")
    auto_monitor = AutoMonitorService(app)
    return auto_monitor

def get_auto_monitor():
    """Retorna a instância do monitoramento"""
    return auto_monitor
"""
        
        # Salvar versão simplificada
        with open('backend/services/auto_monitor_service.py', 'w') as f:
            f.write(conteudo_simples)
        
        logger.info("✅ Serviço auto_monitor_service desativado")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao desativar serviço: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=== INICIANDO DESATIVAÇÃO DE SERVIÇOS PROBLEMÁTICOS ===")
    
    # Desativar auto_monitor_service
    desativar_auto_monitor()
    
    logger.info("=== DESATIVAÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    main()