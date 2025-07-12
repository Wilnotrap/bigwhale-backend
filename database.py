# backend/database.py
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Instância do SQLAlchemy
db = SQLAlchemy()