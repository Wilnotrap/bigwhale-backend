#!/usr/bin/env python3
"""
Script para corrigir dados de datetime corrompidos no banco
"""

import sqlite3
import os
from datetime import datetime

def corrigir_datetime_corrompido():
    """Corrige dados de datetime corrompidos no banco"""
    
    try:
        print("🔧 CORRIGINDO DATETIME CORROMPIDO")
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
        
        # Buscar todos os sinais com datetime corrompido
        cursor.execute("SELECT id, symbol, created_at, updated_at FROM active_signals")
        signals = cursor.fetchall()
        
        print(f"\n📊 Total de sinais: {len(signals)}")
        
        fixed_count = 0
        
        for signal in signals:
            signal_id, symbol, created_at, updated_at = signal
            
            needs_fix = False
            
            # Verificar se created_at está corrompido
            try:
                if created_at:
                    datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                needs_fix = True
                print(f"❌ Sinal {signal_id} ({symbol}) tem created_at corrompido: {created_at}")
            
            # Verificar se updated_at está corrompido
            try:
                if updated_at:
                    datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except:
                needs_fix = True
                print(f"❌ Sinal {signal_id} ({symbol}) tem updated_at corrompido: {updated_at}")
            
            if needs_fix:
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
        
        # Verificar se a correção funcionou
        print(f"\n🎯 VERIFICANDO CORREÇÃO:")
        cursor.execute("SELECT id, symbol, created_at, updated_at FROM active_signals LIMIT 5")
        signals = cursor.fetchall()
        
        for signal in signals:
            signal_id, symbol, created_at, updated_at = signal
            
            try:
                if created_at:
                    datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if updated_at:
                    datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                print(f"   ✅ {symbol}: datetime válido")
            except Exception as e:
                print(f"   ❌ {symbol}: ainda corrompido - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_datetime_corrompido() 