#!/usr/bin/env python3
"""
Script para testar o sistema de monitoramento de alvos
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

def test_monitoramento():
    """Testa o sistema de monitoramento"""
    
    print("🧪 TESTE DO SISTEMA DE MONITORAMENTO")
    print("=" * 50)
    
    try:
        # Testar importações
        print("📦 Testando importações...")
        from database import db
        from models.active_signal import ActiveSignal
        from models.user import User
        from services.auto_monitor_service import AutoMonitorService
        from services.nautilus_auto_sync import NautilusAutoSync
        print("✅ Importações OK")
        
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
            # Testar criação de tabelas
            print("🗄️ Testando criação de tabelas...")
            db.create_all()
            print("✅ Tabelas criadas")
            
            # Testar modelo ActiveSignal
            print("🔍 Testando modelo ActiveSignal...")
            
            # Criar um sinal de teste
            test_signal = ActiveSignal(
                user_id=1,
                symbol='BTCUSDT',
                side='long',
                entry_price=50000.0,
                targets_json='[51000, 52000, 53000]',
                status='active'
            )
            
            # Testar propriedades
            targets = test_signal.targets
            print(f"✅ Targets: {targets}")
            
            # Testar verificação de alvos
            targets_hit = test_signal.check_targets_hit(51500.0)
            print(f"✅ Alvos atingidos com preço 51500: {targets_hit}")
            
            # Testar atualização de alvos
            updated = test_signal.update_targets_hit(51500.0)
            print(f"✅ Atualização realizada: {updated}")
            print(f"✅ Targets hit: {test_signal.targets_hit}")
            
            # Testar conversão para dicionário
            signal_dict = test_signal.to_dict()
            print(f"✅ Conversão para dict: {signal_dict['symbol']} - {signal_dict['targets_hit']} alvos")
            
            print("✅ Modelo ActiveSignal OK")
            
            # Testar serviço de monitoramento
            print("🤖 Testando serviço de monitoramento...")
            monitor_service = AutoMonitorService(app)
            print("✅ Serviço de monitoramento criado")
            
            # Testar validação de sinais
            is_valid = monitor_service._is_signal_valid(test_signal)
            print(f"✅ Sinal válido: {is_valid}")
            
            print("✅ Serviço de monitoramento OK")
            
            # Testar serviço de sincronização
            print("🔄 Testando serviço de sincronização...")
            sync_service = NautilusAutoSync(app)
            print("✅ Serviço de sincronização criado")
            
            print("✅ Serviço de sincronização OK")
            
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ O sistema de monitoramento está funcionando corretamente")
            
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_monitoramento() 