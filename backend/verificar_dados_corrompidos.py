#!/usr/bin/env python3
"""
Script para verificar e corrigir dados corrompidos no banco
"""

import sqlite3
import os
from datetime import datetime

def verificar_e_corrigir_dados():
    """Verifica e corrige dados corrompidos no banco"""
    
    try:
        print("🔍 VERIFICANDO DADOS CORROMPIDOS")
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
        
        # Verificar dados corrompidos na tabela active_signals
        cursor.execute("SELECT id, symbol, side, entry_price, targets, created_at, updated_at, targets_hit FROM active_signals")
        signals = cursor.fetchall()
        
        print(f"\n📊 Total de sinais: {len(signals)}")
        
        corrupted_count = 0
        fixed_count = 0
        
        for signal in signals:
            signal_id, symbol, side, entry_price, targets, created_at, updated_at, targets_hit = signal
            
            # Verificar se created_at ou updated_at estão corrompidos
            needs_fix = False
            
            try:
                if created_at:
                    datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if updated_at:
                    datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except:
                needs_fix = True
                corrupted_count += 1
                print(f"❌ Sinal {signal_id} ({symbol}) tem datetime corrompido")
                print(f"   created_at: {created_at}")
                print(f"   updated_at: {updated_at}")
        
        if corrupted_count > 0:
            print(f"\n🔧 Corrigindo {corrupted_count} sinais corrompidos...")
            
            # Corrigir dados corrompidos
            for signal in signals:
                signal_id, symbol, side, entry_price, targets, created_at, updated_at, targets_hit = signal
                
                try:
                    if created_at:
                        datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if updated_at:
                        datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                except:
                    # Corrigir com timestamp atual
                    now = datetime.utcnow().isoformat()
                    
                    cursor.execute("""
                        UPDATE active_signals 
                        SET created_at = ?, updated_at = ?
                        WHERE id = ?
                    """, (now, now, signal_id))
                    
                    fixed_count += 1
                    print(f"✅ Sinal {signal_id} ({symbol}) corrigido")
            
            # Commit das correções
            conn.commit()
            print(f"\n✅ {fixed_count} sinais corrigidos com sucesso")
        
        else:
            print("✅ Nenhum dado corrompido encontrado")
        
        # Verificar estrutura dos alvos
        print(f"\n🎯 VERIFICANDO ESTRUTURA DOS ALVOS:")
        for signal in signals:
            signal_id, symbol, side, entry_price, targets, created_at, updated_at, targets_hit = signal
            
            try:
                import json
                targets_list = json.loads(targets) if targets else []
                print(f"   {symbol}: {len(targets_list)} alvos, {targets_hit} atingidos")
                
                if targets_list:
                    print(f"      Alvos: {targets_list}")
                    
                    # Verificar se algum alvo foi atingido
                    current_price = entry_price  # Usar preço de entrada como referência
                    
                    for i, target_price in enumerate(targets_list):
                        is_hit = False
                        if side.lower() == 'long':
                            is_hit = current_price >= target_price
                        else:
                            is_hit = current_price <= target_price
                        
                        status = "✓" if is_hit else "⏳"
                        print(f"         {i+1}. ${target_price:.6f} - {status}")
                
            except Exception as e:
                print(f"   ❌ Erro ao processar alvos de {symbol}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_e_corrigir_dados() 