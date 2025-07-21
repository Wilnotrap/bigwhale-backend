#!/bin/bash
# Script para corrigir problemas no Render imediatamente
# Este script deve ser executado diretamente no ambiente do Render

echo "=== INICIANDO CORREÇÃO DIRETA NO RENDER ==="

# Instalar psycopg2-binary
echo "Instalando psycopg2-binary..."
pip install psycopg2-binary==2.9.9

# Executar script de correção
echo "Executando script de correção..."
python correcao_direta_render.py

# Criar tabela active_signals diretamente
echo "Criando tabela active_signals diretamente..."
python -c "
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Definir o caminho do banco SQLite no Render
if os.environ.get('RENDER'):
    db_path = '/tmp/site.db'
else:
    db_path = os.path.join(os.getcwd(), 'instance', 'site.db')

# Criar engine e sessão
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Definir modelo ActiveSignal
class ActiveSignal(Base):
    __tablename__ = 'active_signals'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, nullable=True)
    targets = Column(String(500), nullable=True)
    targets_hit = Column(Integer, default=0)

# Criar tabela
Base.metadata.create_all(engine)
print('Tabela active_signals criada com sucesso!')
"

# Inicializar banco de dados
echo "Inicializando banco de dados..."
python init_db.py

echo "=== CORREÇÃO DIRETA CONCLUÍDA ==="
echo "Reinicie a aplicação no Render para aplicar as correções"