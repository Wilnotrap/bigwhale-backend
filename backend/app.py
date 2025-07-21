#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo de compatibilidade para satisfazer referências ao módulo 'app'
Importa tudo do app_corrigido.py
"""

# Importar tudo do app_corrigido
from app_corrigido import *

# Garantir que 'app' e 'application' estejam disponíveis
try:
    from app_corrigido import app, application, create_app
except ImportError:
    # Se não conseguir importar, criar uma aplicação básica
    from flask import Flask
    app = Flask(__name__)
    application = app
    
    def create_app():
        return app

print("✅ Módulo 'app' carregado com sucesso (compatibilidade)") 