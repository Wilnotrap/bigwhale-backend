#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a segurança do projeto antes do deploy para produção
"""

import os
import sys
import re
import json
from pathlib import Path

def check_env_variables():
    """Verifica se as variáveis de ambiente necessárias estão definidas"""
    required_vars = [
        'FLASK_SECRET_KEY',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente necessárias não definidas: {', '.join(missing_vars)}")
        print("   Defina essas variáveis no dashboard do Render ou no arquivo .env")
        return False
    
    print("✅ Variáveis de ambiente necessárias definidas")
    return True

def check_secret_keys():
    """Verifica se há chaves secretas hardcoded no código"""
    files_to_check = []
    for ext in ['.py', '.js', '.json']:
        files_to_check.extend(Path('.').glob(f'**/*{ext}'))
    
    # Padrões para detectar possíveis chaves secretas
    patterns = [
        r'SECRET_KEY\s*=\s*["\'](?!os\.environ\.get)[^"\']+["\']',
        r'API_KEY\s*=\s*["\'](?!os\.environ\.get)[^"\']+["\']',
        r'PASSWORD\s*=\s*["\'](?!os\.environ\.get)[^"\']+["\']',
        r'TOKEN\s*=\s*["\'](?!os\.environ\.get)[^"\']+["\']'
    ]
    
    issues_found = False
    for file_path in files_to_check:
        if 'node_modules' in str(file_path) or 'venv' in str(file_path) or '.git' in str(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"❌ Possível chave secreta hardcoded em {file_path}:")
                        for match in matches:
                            print(f"   - {match}")
                        issues_found = True
        except Exception as e:
            print(f"Erro ao verificar {file_path}: {e}")
    
    if not issues_found:
        print("✅ Nenhuma chave secreta hardcoded encontrada")
        return True
    
    return False

def check_debug_mode():
    """Verifica se o modo de debug está ativado"""
    files_to_check = list(Path('.').glob('**/*.py'))
    
    issues_found = False
    for file_path in files_to_check:
        if 'node_modules' in str(file_path) or 'venv' in str(file_path) or '.git' in str(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'debug=True' in content:
                    print(f"❌ Modo de debug ativado em {file_path}")
                    issues_found = True
        except Exception as e:
            print(f"Erro ao verificar {file_path}: {e}")
    
    if not issues_found:
        print("✅ Modo de debug desativado")
        return True
    
    return False

def check_cors_configuration():
    """Verifica a configuração de CORS"""
    files_to_check = list(Path('.').glob('**/*.py'))
    
    cors_configured = False
    for file_path in files_to_check:
        if 'node_modules' in str(file_path) or 'venv' in str(file_path) or '.git' in str(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'CORS(' in content:
                    cors_configured = True
                    
                    # Verificar se CORS está configurado corretamente
                    if 'CORS(app)' in content and 'origins=' not in content:
                        print("⚠️ CORS configurado sem restrição de origem")
                        return False
        except Exception as e:
            print(f"Erro ao verificar {file_path}: {e}")
    
    if cors_configured:
        print("✅ CORS configurado corretamente")
        return True
    
    print("❌ CORS não configurado")
    return False

def check_database_connection():
    """Verifica a conexão com o banco de dados"""
    try:
        from app import create_app
        from database import db
        
        app = create_app()
        with app.app_context():
            db.engine.connect()
            print("✅ Conexão com o banco de dados estabelecida com sucesso")
            return True
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False

def main():
    """Função principal"""
    print("🔒 Verificando segurança do projeto para produção...\n")
    
    checks = [
        check_env_variables,
        check_secret_keys,
        check_debug_mode,
        check_cors_configuration
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 Todas as verificações de segurança passaram! O projeto está pronto para produção.")
        return 0
    else:
        print("⚠️ Algumas verificações de segurança falharam. Corrija os problemas antes de fazer o deploy para produção.")
        return 1

if __name__ == '__main__':
    sys.exit(main())