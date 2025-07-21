#!/usr/bin/env python3
"""
Script simples para testar o modelo ActiveSignal
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app_corrigido import create_app
    from database import db
    from models.active_signal import ActiveSignal
    
    print("✅ Imports bem-sucedidos")
    
    # Criar app
    app = create_app()
    
    with app.app_context():
        print("✅ App context criado")
        
        # Tentar buscar sinais
        signals = ActiveSignal.query.all()
        print(f"✅ Sinais encontrados: {len(signals)}")
        
        for signal in signals[:3]:  # Primeiros 3
            print(f"  ID: {signal.id}, Symbol: {signal.symbol}, Side: {signal.side}")
            print(f"  Targets: {signal.targets}")
            print(f"  Targets Hit: {signal.targets_hit}")
            print()
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc() 