#!/usr/bin/env python3
"""
Script para corrigir alvos salvos como strings no banco
"""

import sqlite3
import os
import json

def corrigir_alvos_strings():
    """Corrige alvos salvos como strings no banco"""
    
    try:
        print("🔧 CORRIGINDO ALVOS SALVOS COMO STRINGS")
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
        cursor.execute("SELECT id, symbol, targets FROM active_signals")
        signals = cursor.fetchall()
        
        print(f"\n📊 Total de sinais: {len(signals)}")
        
        fixed_count = 0
        
        for signal in signals:
            signal_id, symbol, targets = signal
            
            try:
                # Verificar se targets é uma string JSON
                if targets:
                    targets_list = json.loads(targets)
                    
                    # Verificar se os alvos são strings
                    needs_fix = False
                    for target in targets_list:
                        if isinstance(target, str):
                            needs_fix = True
                            break
                    
                    if needs_fix:
                        print(f"🔧 Corrigindo alvos de {symbol}...")
                        
                        # Converter strings para float
                        targets_fixed = []
                        for target in targets_list:
                            if isinstance(target, str):
                                targets_fixed.append(float(target))
                            else:
                                targets_fixed.append(target)
                        
                        # Atualizar no banco
                        targets_json = json.dumps(targets_fixed)
                        cursor.execute("""
                            UPDATE active_signals 
                            SET targets = ?
                            WHERE id = ?
                        """, (targets_json, signal_id))
                        
                        fixed_count += 1
                        print(f"   ✅ {symbol}: {targets_list} → {targets_fixed}")
                
            except Exception as e:
                print(f"❌ Erro ao processar {symbol}: {e}")
        
        # Commit das correções
        conn.commit()
        print(f"\n✅ {fixed_count} sinais corrigidos com sucesso")
        
        # Verificar se a correção funcionou
        print(f"\n🎯 VERIFICANDO CORREÇÃO:")
        cursor.execute("SELECT id, symbol, targets FROM active_signals")
        signals = cursor.fetchall()
        
        for signal in signals:
            signal_id, symbol, targets = signal
            
            try:
                if targets:
                    targets_list = json.loads(targets)
                    print(f"   {symbol}: {len(targets_list)} alvos")
                    
                    # Verificar tipos
                    all_floats = all(isinstance(t, (int, float)) for t in targets_list)
                    if all_floats:
                        print(f"      ✅ Todos os alvos são números")
                    else:
                        print(f"      ❌ Ainda há strings nos alvos")
                
            except Exception as e:
                print(f"   ❌ Erro ao verificar {symbol}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_alvos_strings() 