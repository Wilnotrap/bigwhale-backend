#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Monitoramento de Credenciais da API
Monitora continuamente a integridade das credenciais dos usuários
e restaura automaticamente quando detecta problemas
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from database import db
from models.user import User
from utils.api_persistence import APIPersistence
from utils.security import decrypt_api_key, encrypt_api_key
from dotenv import load_dotenv

class CredentialMonitor:
    """Serviço de monitoramento de credenciais"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.api_persistence = APIPersistence()
        self.monitoring = False
        self.monitor_thread = None
        self.check_interval = 60  # Verificar a cada 1 minuto
        self.last_check = {}
        self.failed_users = set()
        
        # Configurar logging
        self.logger = logging.getLogger('credential_monitor')
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo de log
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.FileHandler('logs/credential_monitor.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def init_app(self, app: Flask):
        """Inicializa o monitor com a aplicação Flask"""
        self.app = app
        
        # Registrar comandos CLI
        @app.cli.command()
        def start_credential_monitor():
            """Inicia o monitoramento de credenciais"""
            self.start_monitoring()
        
        @app.cli.command()
        def stop_credential_monitor():
            """Para o monitoramento de credenciais"""
            self.stop_monitoring()
        
        @app.cli.command()
        def check_credentials_now():
            """Executa verificação imediata das credenciais"""
            with app.app_context():
                self.check_all_users_credentials()
    
    def start_monitoring(self):
        """Inicia o monitoramento contínuo"""
        if self.monitoring:
            self.logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("🔍 Monitoramento de credenciais iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento contínuo"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("⏹️ Monitoramento de credenciais parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring:
            try:
                if self.app:
                    with self.app.app_context():
                        self.check_all_users_credentials()
                else:
                    self.logger.error("App Flask não configurado")
                
                # Aguardar próxima verificação
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(30)  # Aguardar 30s antes de tentar novamente
    
    def check_all_users_credentials(self):
        """Verifica as credenciais de todos os usuários"""
        try:
            # Buscar usuários com credenciais da API
            users = User.query.filter(
                (User.bitget_api_key_encrypted.isnot(None)) |
                (User.bitget_api_secret_encrypted.isnot(None)) |
                (User.bitget_passphrase_encrypted.isnot(None))
            ).all()
            
            self.logger.info(f"🔍 Verificando credenciais de {len(users)} usuários")
            
            for user in users:
                self.check_user_credentials(user)
            
            # Log de status geral
            if self.failed_users:
                self.logger.warning(f"⚠️ {len(self.failed_users)} usuários com problemas nas credenciais")
            else:
                self.logger.info("✅ Todas as credenciais estão íntegras")
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar credenciais dos usuários: {e}")
    
    def check_user_credentials(self, user: User) -> Dict[str, any]:
        """Verifica as credenciais de um usuário específico"""
        user_id = user.id
        user_email = user.email
        
        try:
            # Validar credenciais atuais
            validation_result = self.api_persistence.validate_user_credentials(user_id)
            
            if validation_result['valid']:
                # Credenciais OK - remover da lista de falhas se estava lá
                if user_id in self.failed_users:
                    self.failed_users.remove(user_id)
                    self.logger.info(f"✅ Credenciais do usuário {user_email} foram restauradas")
                
                self.last_check[user_id] = datetime.now()
                return validation_result
            
            # Credenciais com problema
            self.logger.warning(f"⚠️ Problema nas credenciais do usuário {user_email}: {validation_result['error']}")
            
            # Tentar restaurar automaticamente
            if self.attempt_credential_restoration(user):
                self.logger.info(f"🔧 Credenciais do usuário {user_email} restauradas automaticamente")
                if user_id in self.failed_users:
                    self.failed_users.remove(user_id)
            else:
                self.failed_users.add(user_id)
                self.logger.error(f"❌ Falha ao restaurar credenciais do usuário {user_email}")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar credenciais do usuário {user_email}: {e}")
            self.failed_users.add(user_id)
            return {'valid': False, 'error': str(e)}
    
    def attempt_credential_restoration(self, user: User) -> bool:
        """Tenta restaurar as credenciais de um usuário"""
        user_id = user.id
        
        try:
            # Buscar backups disponíveis
            backups = self.api_persistence.get_user_backups(user_id)
            
            if not backups:
                self.logger.warning(f"Nenhum backup encontrado para usuário {user.email}")
                return False
            
            # Tentar restaurar do backup mais recente
            latest_backup = backups[0]
            
            self.logger.info(f"🔄 Tentando restaurar do backup: {latest_backup['filename']}")
            
            success = self.api_persistence.restore_user_credentials(user_id, latest_backup['path'])
            
            if success:
                # Verificar se a restauração funcionou
                validation = self.api_persistence.validate_user_credentials(user_id)
                if validation['valid']:
                    self.logger.info(f"✅ Restauração bem-sucedida para usuário {user.email}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro na tentativa de restauração: {e}")
            return False
    
    def secure_save_credentials(self, user_id: int, api_key: str, api_secret: str, passphrase: str) -> bool:
        """Salva credenciais de forma segura com backup"""
        try:
            user = User.query.get(user_id)
            if not user:
                self.logger.error(f"Usuário {user_id} não encontrado")
                return False
            
            # Criar backup antes de salvar
            self.api_persistence.backup_user_credentials(user_id)
            
            # Criptografar e salvar
            user.bitget_api_key_encrypted = encrypt_api_key(api_key)
            user.bitget_api_secret_encrypted = encrypt_api_key(api_secret)
            user.bitget_passphrase_encrypted = encrypt_api_key(passphrase)
            
            db.session.commit()
            
            # Validar se foi salvo corretamente
            validation = self.api_persistence.validate_user_credentials(user_id)
            if validation['valid']:
                self.logger.info(f"✅ Credenciais salvas com sucesso para usuário {user.email}")
                return True
            else:
                self.logger.error(f"❌ Falha na validação após salvar credenciais: {validation['error']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar credenciais: {e}")
            return False
    
    def get_monitoring_status(self) -> Dict[str, any]:
        """Retorna o status atual do monitoramento"""
        return {
            'monitoring': self.monitoring,
            'failed_users_count': len(self.failed_users),
            'failed_users': list(self.failed_users),
            'last_checks': {str(k): v.isoformat() for k, v in self.last_check.items()}
        }
    
    def force_check_user(self, user_id: int) -> Dict[str, any]:
        """Força verificação de um usuário específico"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'valid': False, 'error': 'Usuário não encontrado'}
            
            return self.check_user_credentials(user)
        except Exception as e:
            return {'valid': False, 'error': str(e)}

credential_monitor = CredentialMonitor()