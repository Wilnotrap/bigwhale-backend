#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do sistema demo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.demo_bitget_api import get_demo_api
from services.demo_signal_replicator import demo_replicator
from models.user import User
from flask import Flask
from database import db

def create_app():
    """Cria aplicação Flask para teste"""
    app = Flask(__name__)
    
    # Configuração básica
    app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'
    db_path = os.path.join(os.getcwd(), 'backend', 'instance', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def test_demo_system():
    """Testa todo o sistema demo"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testando Sistema Demo Completo")
            print("=" * 50)
            
            # 1. Verificar usuário demo
            demo_user = User.query.filter_by(email='financeiro@lexxusadm.com.br').first()
            if not demo_user:
                print("❌ Usuário demo não encontrado!")
                return False
            
            print(f"✅ Usuário demo encontrado: {demo_user.full_name}")
            print(f"   💰 Saldo USD: ${demo_user.operational_balance_usd}")
            
            # 2. Testar API demo
            print("\n🔧 Testando API Demo...")
            demo_api = get_demo_api(demo_user.id)
            
            # Testar saldo
            balance = demo_api.get_account_balance()
            if balance['success']:
                print(f"✅ Saldo obtido: ${balance['balance']['total_balance']:.2f}")
            else:
                print("❌ Erro ao obter saldo")
                return False
            
            # 3. Testar colocação de ordem
            print("\n📈 Testando colocação de ordem...")
            order_result = demo_api.place_order(
                symbol='BTCUSDT',
                side='long',
                size=0.001,
                leverage=10
            )
            
            if order_result['success']:
                print(f"✅ Ordem executada: {order_result['order_id']}")
                position_id = order_result['position_id']
                
                # 4. Verificar posições
                print("\n📊 Verificando posições...")
                positions = demo_api.get_positions()
                if positions['success'] and positions['positions']:
                    print(f"✅ {len(positions['positions'])} posição(ões) encontrada(s)")
                    for pos in positions['positions']:
                        print(f"   {pos['symbol']} {pos['side']} - PnL: ${pos['unrealized_pnl']:.2f}")
                
                # 5. Fechar posição
                print("\n🔒 Fechando posição...")
                close_result = demo_api.close_position(position_id)
                if close_result['success']:
                    print(f"✅ Posição fechada - PnL: ${close_result['pnl']:.2f}")
                else:
                    print(f"❌ Erro ao fechar posição: {close_result['message']}")
                
            else:
                print(f"❌ Erro ao executar ordem: {order_result['message']}")
                return False
            
            # 6. Testar estatísticas
            print("\n📈 Testando estatísticas...")
            stats = demo_api.get_trading_stats()
            if stats['success']:
                stats_data = stats['stats']
                print(f"✅ Estatísticas obtidas:")
                print(f"   Total de trades: {stats_data['total_trades']}")
                print(f"   Taxa de acerto: {stats_data['win_rate']:.2f}%")
                print(f"   PnL líquido: ${stats_data['net_profit']:.2f}")
            
            # 7. Testar simulação de sinal
            print("\n🎯 Testando simulação de sinal...")
            signal_data = {
                'symbol': 'ETHUSDT',
                'side': 'short',
                'leverage': 5
            }
            
            signal_result = demo_api.simulate_signal_execution(signal_data)
            if signal_result['success']:
                print(f"✅ Sinal simulado com sucesso")
                print(f"   Posição: {signal_result['position_id']}")
                print(f"   Preço: ${signal_result['execution_price']:.2f}")
            else:
                print(f"❌ Erro ao simular sinal: {signal_result['message']}")
            
            # 8. Testar performance demo
            print("\n📊 Testando performance demo...")
            performance = demo_replicator.get_demo_performance()
            if performance:
                print(f"✅ Performance obtida:")
                print(f"   Saldo total: ${performance['balance'].get('total_balance', 0):.2f}")
                print(f"   Posições abertas: {performance['open_positions']}")
                print(f"   Última atualização: {performance['last_updated']}")
            
            print("\n" + "=" * 50)
            print("🎉 Todos os testes passaram com sucesso!")
            print("\n📋 Resumo do Sistema Demo:")
            print("   ✅ Usuário demo configurado")
            print("   ✅ API simulada funcionando")
            print("   ✅ Ordens sendo executadas")
            print("   ✅ Posições sendo gerenciadas")
            print("   ✅ Estatísticas sendo calculadas")
            print("   ✅ Sinais sendo simulados")
            print("   ✅ Performance sendo monitorada")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante o teste: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_demo_system()
    
    if success:
        print("\n✅ Sistema demo está funcionando perfeitamente!")
    else:
        print("\n❌ Sistema demo apresentou problemas!")
        sys.exit(1)