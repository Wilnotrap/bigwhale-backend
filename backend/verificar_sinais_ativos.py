#!/usr/bin/env python3
"""
Script para verificar sinais ativos
"""

import sqlite3
import os

def verificar_sinais_ativos():
    """Verifica quantos sinais ativos temos"""
    
    print("🔍 VERIFICANDO SINAIS ATIVOS")
    print("=" * 40)
    
    # Caminho do banco
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
        if not cursor.fetchone():
            print("❌ Tabela 'active_signals' não existe")
            return
        
        # Contar sinais
        cursor.execute("SELECT COUNT(*) FROM active_signals")
        total = cursor.fetchone()[0]
        
        print(f"✅ Total de sinais ativos: {total}")
        
        if total > 0:
            # Mostrar alguns detalhes
            cursor.execute("SELECT id, symbol, side, entry_price, targets_json FROM active_signals LIMIT 5")
            sinais = cursor.fetchall()
            
            print("\n📊 Primeiros 5 sinais:")
            for sinal in sinais:
                print(f"  ID: {sinal[0]}, Symbol: {sinal[1]}, Side: {sinal[2]}, Entry: {sinal[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_sinais_ativos() 