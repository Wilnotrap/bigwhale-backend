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

from services.credential_monitor import credential_monitor, create_monitor_app
from services.secure_api_service import secure_api_service, create_secure_api_app
from dotenv import load_dotenv

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
    
    def start_services(self):
        """Inicia todos os serviços"""
        print("🚀 Iniciando serviços de credenciais...")
        
        try:
            # Carregar variáveis de ambiente
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            load_dotenv(env_path)
            print(f"📁 Carregando configurações de: {env_path}")
            
            # Criar aplicações
            self.monitor_app = create_monitor_app()
            self.api_app = create_secure_api_app()
            
            print("✅ Aplicações criadas com sucesso")
            
            # Iniciar monitoramento em contexto da aplicação
            with self.monitor_app.app_context():
                credential_monitor.start_monitoring()
                print("🔍 Monitoramento de credenciais iniciado")
            
            # Iniciar API em thread separada
            self.api_thread = threading.Thread(
                target=self.run_api_server,
                daemon=True
            )
            self.api_thread.start()
            print("🌐 Servidor de API iniciado em thread separada")
            
            self.running = True
            print("\n" + "="*60)
            print("🎉 SERVIÇOS DE CREDENCIAIS INICIADOS COM SUCESSO!")
            print("="*60)
            print("📊 Monitoramento: Ativo (verificação a cada 1 minuto)")
            print("🔗 API Segura: http://localhost:5001")
            print("📝 Logs: logs/credential_monitor.log")
            print("⏹️  Para parar: Ctrl+C")
            print("="*60 + "\n")
            
            # Manter o processo principal rodando
            self.main_loop()
            
        except Exception as e:
            print(f"❌ Erro ao iniciar serviços: {e}")
            self.stop_services()
            sys.exit(1)
    
    def run_api_server(self):
        """Executa o servidor da API"""
        try:
            self.api_app.run(
                debug=False,
                host='0.0.0.0',
                port=5001,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            print(f"❌ Erro no servidor da API: {e}")
    
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
            
            # Verificar se a thread da API está viva
            if self.api_thread and not self.api_thread.is_alive():
                print("⚠️ Thread da API parou, reiniciando...")
                self.api_thread = threading.Thread(
                    target=self.run_api_server,
                    daemon=True
                )
                self.api_thread.start()
            
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
            
            # A thread da API será finalizada automaticamente
            if self.api_thread and self.api_thread.is_alive():
                print("✅ Servidor da API será finalizado")
            
            print("🏁 Todos os serviços foram parados")
            
        except Exception as e:
            print(f"❌ Erro ao parar serviços: {e}")
    
    def get_status(self):
        """Retorna o status atual dos serviços"""
        return {
            'running': self.running,
            'monitor_status': credential_monitor.get_monitoring_status() if self.monitor_app else None,
            'api_thread_alive': self.api_thread.is_alive() if self.api_thread else False,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Função principal"""
    print("🔐 Nautilus - Gerenciador de Credenciais da API")
    print("=" * 50)
    
    # Verificar se já existe outro processo rodando
    pid_file = 'credential_services.pid'
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Verificar se o processo ainda está rodando (Windows)
            import psutil
            if psutil.pid_exists(old_pid):
                print(f"⚠️ Serviços já estão rodando (PID: {old_pid})")
                print("Para parar o processo existente, use Ctrl+C no terminal onde está rodando")
                return
        except (ValueError, ImportError):
            pass
    
    # Salvar PID atual
    try:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
    except Exception as e:
        print(f"⚠️ Não foi possível salvar PID: {e}")
    
    # Criar e iniciar gerenciador
    manager = CredentialServicesManager()
    
    try:
        manager.start_services()
    finally:
        # Limpar arquivo PID
        try:
            if os.path.exists(pid_file):
                os.remove(pid_file)
        except Exception:
            pass

if __name__ == '__main__':
    main()