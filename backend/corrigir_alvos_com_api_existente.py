#!/usr/bin/env python3
"""
Script para corrigir os alvos usando os preços da API que já está funcionando
"""

import sqlite3
import os
import json

def corrigir_alvos_com_api_existente():
    """Corrige os alvos usando os preços da API existente"""
    
    try:
        print("🔧 CORRIGINDO ALVOS COM API EXISTENTE")
        print("=" * 50)
        
        # Caminho do banco
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado: {db_path}")
            return
        
        print(f"✅ Banco encontrado: {db_path}")
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar todos os sinais
        cursor.execute("SELECT id, symbol, side, entry_price, targets, targets_hit FROM active_signals")
        signals = cursor.fetchall()
        
        print(f"📊 Total de sinais: {len(signals)}")
        
        # Preços atuais da API (baseado nos dados que você mostrou)
        current_prices = {
            'GLMUSDT': 0.2775,
            'TRXUSDT': 0.31985,
            'SFPUSDT': 0.5052,
            'ACXUSDT': 0.1819,
            'XVGUSDT': 0.007123,
            'GUSDT': 0.01302,
            'CVXUSDT': 4.755,
            'BELUSDT': 0.2874,
            'MKRUSDT': 1985.6,
            'VVVUSDT': 3.2,
            'DIAUSDT': 0.4701,  # Da imagem anterior
            'BNBUSDT': 0.0,  # Precisamos do preço atual
            'XTZUSDT': 0.0,  # Precisamos do preço atual
            'DFUSDT': 0.0    # Precisamos do preço atual
        }
        
        total_corrigidos = 0
        
        for signal in signals:
            signal_id, symbol, side, entry_price, targets_json, targets_hit = signal
            
            # Converter targets de JSON para lista
            targets = json.loads(targets_json) if targets_json else []
            
            # Obter preço atual
            current_price = current_prices.get(symbol)
            
            if current_price is None or current_price == 0:
                print(f"⚠️ Preço não disponível para {symbol}")
                continue
            
            # Calcular alvos atingidos corretamente
            targets_hit_correct = 0
            targets_info = []
            
            for i, target_price in enumerate(targets):
                is_hit = False
                if side.lower() == 'long':
                    # Para LONG: alvo é atingido quando preço atual >= preço alvo
                    is_hit = current_price >= target_price
                else:
                    # Para SHORT: alvo é atingido quando preço atual <= preço alvo
                    is_hit = current_price <= target_price
                
                if is_hit:
                    targets_hit_correct += 1
                
                targets_info.append({
                    'target': target_price,
                    'is_hit': is_hit
                })
            
            # Verificar se precisa corrigir
            if targets_hit_correct != targets_hit:
                print(f"🔧 {symbol}: {targets_hit} → {targets_hit_correct} alvos (preço: {current_price})")
                print(f"   Lado: {side}, Entrada: {entry_price}")
                for info in targets_info:
                    status = "✅" if info['is_hit'] else "❌"
                    print(f"   {status} Alvo {info['target']}")
                
                cursor.execute(
                    "UPDATE active_signals SET targets_hit = ? WHERE id = ?",
                    (targets_hit_correct, signal_id)
                )
                total_corrigidos += 1
            else:
                print(f"✅ {symbol}: {targets_hit} alvos (preço: {current_price}) - OK")
        
        # Salvar alterações
        conn.commit()
        conn.close()
        
        print(f"\n📈 RESULTADO:")
        print(f"   Total de sinais verificados: {len(signals)}")
        print(f"   Sinais corrigidos: {total_corrigidos}")
        print(f"   ✅ Correção concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_alvos_com_api_existente() 