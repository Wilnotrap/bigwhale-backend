# backend/database.py
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Instância do SQLAlchemy
db = SQLAlchemy()

# Nota: Os modelos são importados no app_corrigido.py para evitar importação circular