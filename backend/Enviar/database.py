# backend/database.py
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Instância do SQLAlchemy
db = SQLAlchemy()

# Importar modelos para garantir criação das tabelas
from models.user import User
from models.trade import Trade
from models.invite_code import InviteCode