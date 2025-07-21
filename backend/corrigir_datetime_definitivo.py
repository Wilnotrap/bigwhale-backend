#!/usr/bin/env python3
"""
Script definitivo para corrigir todos os problemas de datetime
"""

import sqlite3
import os
from datetime import datetime

def corrigir_datetime_definitivo():
    """Corrige definitivamente todos os problemas de datetime"""
    
    try:
        print("🔧 CORREÇÃO DEFINITIVA DE DATETIME")
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
        cursor.execute("SELECT id, symbol, created_at, updated_at FROM active_signals")
        signals = cursor.fetchall()
        
        print(f"\n📊 Total de sinais: {len(signals)}")
        
        # Forçar correção de todos os sinais
        now = datetime.utcnow().isoformat()
        fixed_count = 0
        
        for signal in signals:
            signal_id, symbol, created_at, updated_at = signal
            
            # Sempre atualizar para garantir consistência
            cursor.execute("""
                UPDATE active_signals 
                SET created_at = ?, updated_at = ?
                WHERE id = ?
            """, (now, now, signal_id))
            
            fixed_count += 1
            print(f"✅ {symbol}: datetime corrigido")
        
        # Commit das correções
        conn.commit()
        print(f"\n✅ {fixed_count} sinais corrigidos com sucesso")
        
        # Verificar se a correção funcionou
        print(f"\n🎯 VERIFICANDO CORREÇÃO:")
        cursor.execute("SELECT symbol, created_at, updated_at FROM active_signals LIMIT 5")
        signals = cursor.fetchall()
        
        for signal in signals:
            symbol, created_at, updated_at = signal
            print(f"   {symbol}: {created_at} / {updated_at}")
        
        conn.close()
        print(f"\n✅ Correção definitiva concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_datetime_definitivo() 