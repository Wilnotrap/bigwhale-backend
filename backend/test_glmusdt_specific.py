#!/usr/bin/env python3
"""
Script para testar especificamente o GLMUSDT e verificar a comparação de alvos
"""

import sqlite3
import os
import json

def test_glmusdt_specific():
    """Testa especificamente o GLMUSDT"""
    
    try:
        print("🎯 TESTANDO GLMUSDT ESPECÍFICO")
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
        
        # Buscar GLMUSDT
        cursor.execute("SELECT id, symbol, side, entry_price, targets, targets_hit FROM active_signals WHERE symbol = 'GLMUSDT'")
        signal = cursor.fetchone()
        
        if not signal:
            print("❌ GLMUSDT não encontrado no banco")
            return
        
        signal_id, symbol, side, entry_price, targets_json, targets_hit = signal
        
        # Converter targets de JSON para lista
        targets = json.loads(targets_json) if targets_json else []
        
        print(f"📊 DADOS DO GLMUSDT:")
        print(f"   Símbolo: {symbol}")
        print(f"   Lado: {side}")
        print(f"   Preço de entrada: {entry_price}")
        print(f"   Alvos: {targets}")
        print(f"   Alvos atingidos (banco): {targets_hit}")
        
        # Preço atual da imagem: 0.2774
        current_price = 0.2774
        print(f"   Preço atual (da imagem): {current_price}")
        
        print(f"\n🎯 ANÁLISE DOS ALVOS:")
        
        targets_hit_count = 0
        for i, target_price in enumerate(targets):
            # Verificar se o alvo foi atingido
            is_hit = False
            if side.lower() == 'long':
                # Para LONG: alvo é atingido quando preço atual >= preço alvo
                is_hit = current_price >= target_price
            else:
                # Para SHORT: alvo é atingido quando preço atual <= preço alvo
                is_hit = current_price <= target_price
            
            status = "✅ ATINGIDO" if is_hit else "❌ NÃO ATINGIDO"
            print(f"   Alvo {i+1}: {target_price} - {status}")
            
            if is_hit:
                targets_hit_count += 1
        
        print(f"\n📈 RESULTADO:")
        print(f"   Alvos atingidos calculados: {targets_hit_count}")
        print(f"   Alvos atingidos no banco: {targets_hit}")
        
        if targets_hit_count != targets_hit:
            print(f"   ❌ DISCREPÂNCIA ENCONTRADA!")
            print(f"   🔧 Atualizando banco...")
            
            cursor.execute(
                "UPDATE active_signals SET targets_hit = ? WHERE id = ?",
                (targets_hit_count, signal_id)
            )
            conn.commit()
            print(f"   ✅ Banco atualizado!")
        else:
            print(f"   ✅ Dados consistentes!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_glmusdt_specific() 