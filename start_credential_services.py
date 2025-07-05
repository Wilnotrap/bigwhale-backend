#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialização dos Serviços de Credenciais
Inicia o monitoramento contínuo e a API segura de credenciais
"""

import os
import sys
import time
import signal
import threading
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.credential_monitor import credential_monitor
from services.secure_api_service import secure_api_service
from dotenv import load_dotenv
from flask import Flask
from database import db

class CredentialServicesManager:
    """Gerenciador dos serviços de credenciais"""
    
    def __init__(self):
        self.monitor_app = None
        self.api_app = None
        self.running = False
        self.api_thread = None
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        print(f"\n🛑 Recebido sinal {signum}, parando serviços...")
        self.stop_services()
        sys.exit(0)
    
    def create_app(self):
        """Cria aplicação Flask"""
        app = Flask(__name__)
        
        # Configurações
        app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
        app.config['AES_ENCRYPTION_KEY'] = os.environ.get('AES_ENCRYPTION_KEY', 'dev-encryption-key')
        
        # Banco de dados
        db_path = '/tmp/site.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicializar extensões
        db.init_app(app)
        
        # Criar tabelas
        with app.app_context():
            db.create_all()
        
        return app
    
    def start_services(self):
        """Inicia todos os serviços"""
        print("🚀 Iniciando serviços de credenciais...")
        
        try:
            # Carregar variáveis de ambiente
            load_dotenv()
            print("📁 Configurações carregadas")
            
            # Criar aplicação
            self.monitor_app = self.create_app()
            print("✅ Aplicação criada com sucesso")
            
            # Inicializar serviços
            credential_monitor.init_app(self.monitor_app)
            secure_api_service.init_app(self.monitor_app)
            
            # Iniciar monitoramento em contexto da aplicação
            with self.monitor_app.app_context():
                credential_monitor.start_monitoring()
                print("🔍 Monitoramento de credenciais iniciado")
            
            self.running = True
            print("\n" + "="*60)
            print("🎉 SERVIÇOS DE CREDENCIAIS INICIADOS COM SUCESSO!")
            print("="*60)
            print("📊 Monitoramento: Ativo (verificação a cada 1 minuto)")
            print("📝 Logs: logs/credential_monitor.log")
            print("⏹️  Para parar: Ctrl+C")
            print("="*60 + "\n")
            
            # Manter o processo principal rodando
            self.main_loop()
            
        except Exception as e:
            print(f"❌ Erro ao iniciar serviços: {e}")
            self.stop_services()
            sys.exit(1)
    
    def main_loop(self):
        """Loop principal do gerenciador"""
        try:
            while self.running:
                # Verificar status dos serviços a cada 30 segundos
                time.sleep(30)
                
                if self.running:
                    self.check_services_health()
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupção detectada")
        finally:
            self.stop_services()
    
    def check_services_health(self):
        """Verifica a saúde dos serviços"""
        try:
            # Verificar se o monitoramento está ativo
            if not credential_monitor.monitoring:
                print("⚠️ Monitoramento parado, reiniciando...")
                with self.monitor_app.app_context():
                    credential_monitor.start_monitoring()
            
            # Log de status (apenas a cada 5 minutos)
            current_time = datetime.now()
            if current_time.minute % 5 == 0 and current_time.second < 30:
                status = credential_monitor.get_monitoring_status()
                failed_count = status.get('failed_users_count', 0)
                if failed_count > 0:
                    print(f"⚠️ {failed_count} usuários com problemas nas credenciais")
                else:
                    print("✅ Todos os serviços funcionando normalmente")
                    
        except Exception as e:
            print(f"❌ Erro na verificação de saúde: {e}")
    
    def stop_services(self):
        """Para todos os serviços"""
        if not self.running:
            return
        
        print("⏹️ Parando serviços de credenciais...")
        self.running = False
        
        try:
            # Parar monitoramento
            credential_monitor.stop_monitoring()
            print("✅ Monitoramento parado")
            
            print("🏁 Todos os serviços foram parados")
            
        except Exception as e:
            print(f"❌ Erro ao parar serviços: {e}")

def main():
    """Função principal"""
    print("🔐 Nautilus - Gerenciador de Credenciais da API")
    print("=" * 50)
    
    manager = CredentialServicesManager()
    manager.start_services()

if __name__ == '__main__':
    main()