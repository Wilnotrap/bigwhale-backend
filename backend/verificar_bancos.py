#!/usr/bin/env python3
"""
Script para verificar os bancos de dados
"""

import sqlite3
import os

def verificar_bancos():
    """Verifica os bancos de dados"""
    
    bancos = ['instance/site.db']
    
    for banco in bancos:
        if os.path.exists(banco):
            try:
                conn = sqlite3.connect(banco)
                cursor = conn.cursor()
                
                # Verificar se a tabela existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM active_signals")
                    count = cursor.fetchone()[0]
                    print(f"✅ {banco}: {count} sinais")
                    
                    # Mostrar alguns sinais
                    cursor.execute("SELECT id, symbol, side, entry_price, targets_hit FROM active_signals LIMIT 3")
                    signals = cursor.fetchall()
                    for signal in signals:
                        print(f"   ID: {signal[0]}, Symbol: {signal[1]}, Side: {signal[2]}, Price: {signal[3]}, Hits: {signal[4]}")
                else:
                    print(f"❌ {banco}: Tabela active_signals não existe")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ {banco}: Erro - {e}")
        else:
            print(f"❌ {banco}: Arquivo não existe")

if __name__ == "__main__":
    verificar_bancos() 