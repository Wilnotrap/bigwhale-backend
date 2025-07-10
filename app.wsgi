#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Importar a aplicação
from app import app as application

if __name__ == "__main__":
    application.run()
