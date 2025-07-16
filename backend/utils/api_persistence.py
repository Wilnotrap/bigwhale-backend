#!/usr/bin/env python3
"""
Sistema de persistência e backup das credenciais da API
"""

import os
import json
# import sqlite3  # Removido - usando apenas PostgreSQL
from datetime import datetime
from typing import Dict, Optional, List
from utils.security import encrypt_api_key, decrypt_api_key
from flask import current_app

class APIPersistence:
    """Classe para gerenciar a persistência das credenciais da API"""
    
    def __init__(self, db_path: str = None):
        print(f"APIPersistence: Inicializando com db_path inicial: {db_path}")
        if db_path is None:
            # Check for RENDER environment variable first
            if os.environ.get('RENDER'):
                self.db_path = '/tmp/site.db'
                print(f"APIPersistence: Ambiente Render detectado, usando db_path: {self.db_path}")
            else:
                # Usar o mesmo caminho do Flask
                try:
                    self.db_path = os.path.join(current_app.instance_path, 'site.db')
                    print(f"APIPersistence: Em contexto Flask, usando db_path: {self.db_path}")
                except RuntimeError:
                    # Fallback se não estiver em contexto do Flask
                    self.db_path = os.path.join('backend', 'instance', 'site.db')
                    print(f"APIPersistence: Fallback, usando db_path: {self.db_path}")
        else:
            self.db_path = db_path
            print(f"APIPersistence: db_path fornecido, usando: {self.db_path}")

        self.backup_dir = 'backups/api_credentials'
        self._ensure_backup_dir()
        print(f"APIPersistence: Finalizado init. DB Path final: {self.db_path}")
    
    def _ensure_backup_dir(self):
        """Garante que o diretório de backup existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_user_credentials(self, user_id: int) -> bool:
        """Backup usando SQLAlchemy (PostgreSQL)"""
        try:
            from models.user import User
            from database import db
            
            # Buscar credenciais do usuário usando SQLAlchemy
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Usuário {user_id} não encontrado para backup")
                return False
            
            # Criar backup
            backup_data = {
                'user_id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'api_key_encrypted': user.bitget_api_key_encrypted,
                'api_secret_encrypted': user.bitget_api_secret_encrypted,
                'passphrase_encrypted': user.bitget_passphrase_encrypted,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'backup_timestamp': datetime.now().isoformat(),
                'backup_type': 'user_credentials'
            }
            
            # Salvar backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_dir}/user_{user_id}_credentials_{timestamp}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Backup das credenciais do usuário {user_id} salvo em: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao fazer backup das credenciais do usuário {user_id}: {e}")
            return False
    
    def restore_user_credentials(self, user_id: int, backup_file: str) -> bool:
        """Restaura credenciais de um backup usando SQLAlchemy (PostgreSQL)"""
        try:
            if not os.path.exists(backup_file):
                print(f"❌ Arquivo de backup não encontrado: {backup_file}")
                return False
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            from models.user import User
            from database import db
            
            # Buscar usuário
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Usuário {user_id} não encontrado para restauração")
                return False
            
            # Restaurar credenciais
            user.bitget_api_key_encrypted = backup_data['api_key_encrypted']
            user.bitget_api_secret_encrypted = backup_data['api_secret_encrypted']
            user.bitget_passphrase_encrypted = backup_data['passphrase_encrypted']
            
            db.session.commit()
            
            print(f"✅ Credenciais do usuário {user_id} restauradas do backup")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar credenciais do usuário {user_id}: {e}")
            return False
    
    def validate_user_credentials(self, user_id: int) -> Dict[str, any]:
        """Valida se as credenciais de um usuário estão íntegras usando SQLAlchemy (PostgreSQL)"""
        try:
            from models.user import User
            
            # Buscar usuário usando SQLAlchemy
            user = User.query.get(user_id)
            
            if not user:
                return {
                    'valid': False,
                    'error': 'Usuário não encontrado',
                    'has_credentials': False
                }
            
            # Verificar se todas as credenciais existem
            api_key_enc = user.bitget_api_key_encrypted
            secret_enc = user.bitget_api_secret_encrypted
            passphrase_enc = user.bitget_passphrase_encrypted
            
            has_all_credentials = all([api_key_enc, secret_enc, passphrase_enc])
            
            if not has_all_credentials:
                return {
                    'valid': False,
                    'error': 'Credenciais incompletas',
                    'has_credentials': False,
                    'missing': {
                        'api_key': not bool(api_key_enc),
                        'secret': not bool(secret_enc),
                        'passphrase': not bool(passphrase_enc)
                    }
                }
            
            # Tentar descriptografar
            try:
                api_key = decrypt_api_key(api_key_enc)
                secret = decrypt_api_key(secret_enc)
                passphrase = decrypt_api_key(passphrase_enc)
                
                decryption_success = all([api_key, secret, passphrase])
                
                return {
                    'valid': decryption_success,
                    'has_credentials': True,
                    'decryption_success': decryption_success,
                    'error': None if decryption_success else 'Falha na descriptografia'
                }
                
            except Exception as e:
                return {
                    'valid': False,
                    'has_credentials': True,
                    'decryption_success': False,
                    'error': f'Erro na descriptografia: {str(e)}'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'Erro na validação: {str(e)}',
                'has_credentials': False
            }
    
    def get_user_backups(self, user_id: int) -> List[Dict[str, any]]:
        """Lista todos os backups disponíveis para um usuário"""
        backups = []
        
        try:
            if not os.path.exists(self.backup_dir):
                return backups
            
            # Buscar arquivos de backup do usuário
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(f"user_{user_id}_credentials_") and filename.endswith('.json'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    
                    try:
                        with open(backup_path, 'r') as f:
                            backup_data = json.load(f)
                        
                        backups.append({
                            'filename': filename,
                            'path': backup_path,
                            'timestamp': backup_data.get('backup_timestamp'),
                            'user_email': backup_data.get('email'),
                            'size': os.path.getsize(backup_path)
                        })
                        
                    except Exception as e:
                        print(f"⚠️ Erro ao ler backup {filename}: {e}")
            
            # Ordenar por timestamp (mais recente primeiro)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"❌ Erro ao listar backups do usuário {user_id}: {e}")
        
        return backups
    
    def auto_backup_on_update(self, user_id: int) -> bool:
        """Faz backup automático antes de atualizar credenciais"""
        print(f"🔄 Fazendo backup automático das credenciais do usuário {user_id}")
        return self.backup_user_credentials(user_id)
    
    def cleanup_old_backups(self, user_id: int, keep_last: int = 5) -> int:
        """Remove backups antigos, mantendo apenas os mais recentes"""
        backups = self.get_user_backups(user_id)
        
        if len(backups) <= keep_last:
            return 0
        
        # Remover backups antigos
        removed_count = 0
        for backup in backups[keep_last:]:
            try:
                os.remove(backup['path'])
                removed_count += 1
                print(f"🗑️ Backup antigo removido: {backup['filename']}")
            except Exception as e:
                print(f"⚠️ Erro ao remover backup {backup['filename']}: {e}")
        
        return removed_count

# Instância global para uso em outras partes da aplicação
api_persistence = APIPersistence() 