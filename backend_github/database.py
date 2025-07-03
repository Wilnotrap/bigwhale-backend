from flask_sqlalchemy import SQLAlchemy
import os

# Instância do SQLAlchemy
db = SQLAlchemy()

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()