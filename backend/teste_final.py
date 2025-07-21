#!/usr/bin/env python3
"""
Teste final para verificar se tudo está funcionando
"""

import requests
import json

def teste_final():
    """Teste final do sistema"""
    
    print("🧪 TESTE FINAL DO SISTEMA")
    print("=" * 50)
    
    try:
        # Testar endpoint sem autenticação
        response = requests.get("http://localhost:5000/api/dashboard/nautilus-operacional/active-signals-with-targets")
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando!")
            print(f"📊 Total de sinais: {data.get('total_signals', 0)}")
            print(f"🎯 Alvos atingidos: {data.get('targets_hit', 0)}")
            print(f"📈 Sinais com alvos: {data.get('signals_with_targets', 0)}")
            
            signals = data.get('signals', [])
            print(f"\n🎯 SINAIS ATIVOS ({len(signals)}):")
            for signal in signals:
                print(f"   {signal['symbol']} ({signal['side']}) - Preço: {signal['entry_price']}, Alvos: {signal['targets_hit']}/{signal['total_targets']}")
                
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")

if __name__ == "__main__":
    teste_final() 