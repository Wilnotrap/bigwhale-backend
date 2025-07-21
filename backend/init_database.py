#!/usr/bin/env python3
"""
Script para inicializar o banco de dados corretamente
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

from database import db
from models.user import User
from models.active_signal import ActiveSignal

def init_database():
    """Inicializa o banco de dados"""
    
    print("🗄️ INICIALIZANDO BANCO DE DADOS")
    print("=" * 50)
    
    # Criar diretório instance se não existir
    instance_path = Path("instance")
    instance_path.mkdir(exist_ok=True)
    
    # Configurar Flask app
    from flask import Flask
    app = Flask(__name__)
    
    # Configuração do banco
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'
    
    # Inicializar banco
    db.init_app(app)
    
    with app.app_context():
        # Criar todas as tabelas
        print("📋 Criando tabelas...")
        db.create_all()
        
        # Verificar se as tabelas foram criadas
        tables = db.engine.table_names()
        print(f"✅ Tabelas criadas: {tables}")
        
        # Verificar se há dados na tabela active_signals
        signals_count = ActiveSignal.query.count()
        print(f"📊 Sinais ativos no banco: {signals_count}")
        
        if signals_count > 0:
            print("🔍 Verificando integridade dos dados...")
            
            # Verificar registros com problemas
            signals = ActiveSignal.query.all()
            corrupted_count = 0
            
            for signal in signals:
                try:
                    # Testar conversão de datetime
                    if signal.created_at:
                        _ = signal.created_at.isoformat()
                    if signal.updated_at:
                        _ = signal.updated_at.isoformat()
                    if signal.completed_at:
                        _ = signal.completed_at.isoformat()
                    
                    # Testar conversão de targets
                    _ = signal.targets
                    
                except Exception as e:
                    print(f"❌ Sinal {signal.id} corrompido: {e}")
                    corrupted_count += 1
                    # Remover sinal corrompido
                    db.session.delete(signal)
            
            if corrupted_count > 0:
                db.session.commit()
                print(f"🧹 {corrupted_count} sinais corrompidos removidos")
        
        print("✅ Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_database() 