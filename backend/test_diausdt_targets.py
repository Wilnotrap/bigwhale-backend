#!/usr/bin/env python3
"""
Script para testar especificamente os alvos do DIAUSDT
"""

import sqlite3
import os
import json
from datetime import datetime

def test_diausdt_targets():
    """Testa os alvos do DIAUSDT"""
    
    try:
        print("🎯 TESTANDO ALVOS DO DIAUSDT")
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
        
        # Buscar DIAUSDT
        cursor.execute("SELECT id, symbol, side, entry_price, targets, targets_hit FROM active_signals WHERE symbol = 'DIAUSDT'")
        signal = cursor.fetchone()
        
        if not signal:
            print("❌ DIAUSDT não encontrado no banco")
            return
        
        signal_id, symbol, side, entry_price, targets, targets_hit = signal
        
        print(f"\n📊 DADOS DO DIAUSDT:")
        print(f"   ID: {signal_id}")
        print(f"   Símbolo: {symbol}")
        print(f"   Lado: {side}")
        print(f"   Preço de entrada: {entry_price}")
        print(f"   Alvos atingidos: {targets_hit}")
        
        # Parsear alvos
        targets_list = json.loads(targets) if targets else []
        print(f"   Total de alvos: {len(targets_list)}")
        print(f"   Alvos: {targets_list}")
        
        # Preços atuais (baseado na imagem)
        current_price = 0.4701  # Preço atual mostrado na imagem
        
        print(f"\n🎯 ANÁLISE DOS ALVOS:")
        print(f"   Preço atual: {current_price}")
        print(f"   Preço de entrada: {entry_price}")
        print(f"   Diferença: {((current_price - entry_price) / entry_price) * 100:.2f}%")
        
        # Verificar cada alvo
        targets_hit_count = 0
        for i, target_price in enumerate(targets_list):
            is_hit = False
            
            if side.lower() == 'short':
                # Para SHORT: alvo é atingido quando preço atual <= preço alvo
                is_hit = current_price <= target_price
            else:
                # Para LONG: alvo é atingido quando preço atual >= preço alvo
                is_hit = current_price >= target_price
            
            if is_hit:
                targets_hit_count += 1
            
            status = "✓ ATINGIDO" if is_hit else "⏳ PENDENTE"
            distance = ((current_price - target_price) / target_price) * 100
            
            print(f"   Alvo {i+1}: ${target_price:.4f} - {status} (distância: {distance:.2f}%)")
        
        print(f"\n📈 RESUMO:")
        print(f"   Alvos atingidos calculados: {targets_hit_count}")
        print(f"   Alvos atingidos no banco: {targets_hit}")
        
        if targets_hit_count != targets_hit:
            print(f"   ❌ DISCREPÂNCIA ENCONTRADA!")
            print(f"   🔧 Atualizando banco...")
            
            cursor.execute("""
                UPDATE active_signals 
                SET targets_hit = ?, updated_at = ?
                WHERE id = ?
            """, (targets_hit_count, datetime.utcnow().isoformat(), signal_id))
            
            conn.commit()
            print(f"   ✅ Banco atualizado!")
        else:
            print(f"   ✅ Dados consistentes!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_diausdt_targets() 