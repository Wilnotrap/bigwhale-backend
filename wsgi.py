#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI entry point for Render deployment
"""

import sys
import os

# Debug: mostrar informações do ambiente
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

# Adicionar o diretório backend ao Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')

print(f"Current dir: {current_dir}")
print(f"Backend path: {backend_path}")
print(f"Backend exists: {os.path.exists(backend_path)}")

# Verificar se app.py existe
app_file = os.path.join(backend_path, 'app.py')
print(f"App file: {app_file}")
print(f"App file exists: {os.path.exists(app_file)}")

# Adicionar ao path
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

print(f"Updated Python path: {sys.path[:3]}")

# Tentar importar
try:
    print("Tentando importar app...")
    import app
    print("✅ App importado com sucesso")
    application = app.application
    print("✅ Application obtida com sucesso")
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    # Fallback: tentar importação direta
    try:
        print("Tentando fallback...")
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
        import app
        application = app.application
        print("✅ Fallback funcionou")
    except Exception as e2:
        print(f"❌ Fallback falhou: {e2}")
        raise

if __name__ == "__main__":
    application.run()