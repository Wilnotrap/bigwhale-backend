#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point for Render deployment
Backend BigWhale - Versão Otimizada
"""

import sys
import os

# Debug: mostrar informações do ambiente
print(f"🔍 Current working directory: {os.getcwd()}")
print(f"🔍 Python path: {sys.path[:3]}")

# Adicionar o diretório atual ao Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"🔍 Current dir: {current_dir}")

# Verificar se o arquivo app_render_fixed.py existe
app_file = os.path.join(current_dir, 'app_render_fixed.py')
print(f"🔍 App file: {app_file}")
print(f"🔍 App file exists: {os.path.exists(app_file)}")

# Tentar importar a aplicação
try:
    print("🚀 Tentando importar app_render_fixed...")
    from app_render_fixed import application
    print("✅ Application importada com sucesso!")
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    # Fallback para app_minimal
    try:
        print("🔄 Tentando fallback para app_minimal...")
        from app_minimal import application
        print("✅ Fallback funcionou!")
    except Exception as e2:
        print(f"❌ Fallback falhou: {e2}")
        raise

if __name__ == "__main__":
    application.run()