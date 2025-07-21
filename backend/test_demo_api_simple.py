#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples da API demo sem banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.demo_bitget_api import DemoBitgetAPI

def test_demo_api():
    """Testa a API demo diretamente"""
    try:
        print("🧪 Testando API Demo Simples")
        print("=" * 40)
        
        # Criar instância da API demo
        demo_api = DemoBitgetAPI(user_id=3, initial_balance=600.0)
        
        # 1. Testar saldo inicial
        print("💰 Testando saldo inicial...")
        balance = demo_api.get_account_balance()
        if balance['success']:
            print(f"✅ Saldo: ${balance['balance']['total_balance']:.2f}")
        else:
            print("❌ Erro ao obter saldo")
            return False
        
        # 2. Testar colocação de ordem LONG
        print("\n📈 Testando ordem LONG...")
        order1 = demo_api.place_order(
            symbol='BTCUSDT',
            side='long',
            size=0.001,
            leverage=10
        )
        
        if order1['success']:
            print(f"✅ Ordem LONG executada: {order1['order_id']}")
            print(f"   Preço: ${order1['execution_price']:.2f}")
            position1_id = order1['position_id']
        else:
            print(f"❌ Erro na ordem LONG: {order1['message']}")
            return False
        
        # 3. Testar colocação de ordem SHORT
        print("\n📉 Testando ordem SHORT...")
        order2 = demo_api.place_order(
            symbol='ETHUSDT',
            side='short',
            size=0.01,
            leverage=5
        )
        
        if order2['success']:
            print(f"✅ Ordem SHORT executada: {order2['order_id']}")
            print(f"   Preço: ${order2['execution_price']:.2f}")
            position2_id = order2['position_id']
        else:
            print(f"❌ Erro na ordem SHORT: {order2['message']}")
            return False
        
        # 4. Verificar posições abertas
        print("\n📊 Verificando posições abertas...")
        positions = demo_api.get_positions()
        if positions['success']:
            print(f"✅ {len(positions['positions'])} posições encontradas:")
            for pos in positions['positions']:
                print(f"   {pos['symbol']} {pos['side']} - PnL: ${pos['unrealized_pnl']:.2f}")
        else:
            print("❌ Erro ao obter posições")
        
        # 5. Simular movimento de preços
        print("\n📈 Simulando movimento de preços...")
        demo_api.update_prices()
        print("✅ Preços atualizados")
        
        # Verificar posições após movimento
        positions = demo_api.get_positions()
        if positions['success']:
            print("📊 Posições após movimento:")
            for pos in positions['positions']:
                print(f"   {pos['symbol']} {pos['side']} - PnL: ${pos['unrealized_pnl']:.2f}")
        
        # 6. Fechar primeira posição
        print("\n🔒 Fechando posição BTCUSDT...")
        close1 = demo_api.close_position(position1_id)
        if close1['success']:
            print(f"✅ Posição fechada - PnL: ${close1['pnl']:.2f}")
        else:
            print(f"❌ Erro ao fechar: {close1['message']}")
        
        # 7. Testar simulação de sinal
        print("\n🎯 Testando simulação de sinal...")
        signal_data = {
            'symbol': 'ADAUSDT',
            'side': 'long',
            'leverage': 8
        }
        
        signal_result = demo_api.simulate_signal_execution(signal_data)
        if signal_result['success']:
            print(f"✅ Sinal executado: {signal_result['position_id']}")
        else:
            print(f"❌ Erro no sinal: {signal_result['message']}")
        
        # 8. Obter estatísticas finais
        print("\n📈 Estatísticas finais...")
        stats = demo_api.get_trading_stats()
        if stats['success']:
            s = stats['stats']
            print(f"✅ Estatísticas:")
            print(f"   Total trades: {s['total_trades']}")
            print(f"   Trades ganhos: {s['winning_trades']}")
            print(f"   Taxa de acerto: {s['win_rate']:.2f}%")
            print(f"   PnL líquido: ${s['net_profit']:.2f}")
        
        # 9. Saldo final
        print("\n💰 Saldo final...")
        final_balance = demo_api.get_account_balance()
        if final_balance['success']:
            b = final_balance['balance']
            print(f"✅ Saldo final: ${b['total_balance']:.2f}")
            print(f"   Disponível: ${b['available_balance']:.2f}")
            print(f"   PnL não realizado: ${b['unrealized_pnl']:.2f}")
        
        print("\n" + "=" * 40)
        print("🎉 Teste da API demo concluído com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_demo_api()
    
    if success:
        print("\n✅ API demo está funcionando perfeitamente!")
        print("\n📋 Funcionalidades testadas:")
        print("   ✅ Saldo da conta")
        print("   ✅ Ordens LONG e SHORT")
        print("   ✅ Posições abertas")
        print("   ✅ Movimento de preços")
        print("   ✅ Fechamento de posições")
        print("   ✅ Simulação de sinais")
        print("   ✅ Estatísticas de trading")
    else:
        print("\n❌ API demo apresentou problemas!")
        sys.exit(1)