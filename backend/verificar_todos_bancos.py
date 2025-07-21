#!/usr/bin/env python3
"""
Script para verificar sinais em todos os bancos de dados
"""

import sqlite3
import os

def verificar_todos_bancos():
    """Verifica sinais em todos os bancos de dados"""
    
    print("🔍 VERIFICANDO TODOS OS BANCOS DE DADOS")
    print("=" * 50)
    
    bancos = [
        'instance/site.db',
        'instance/site.db'
    ]
    
    for banco in bancos:
        db_path = os.path.join(os.path.dirname(__file__), banco)
        
        if not os.path.exists(db_path):
            print(f"❌ {banco}: Não encontrado")
            continue
        
        try:
            # Conectar ao banco
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
            if not cursor.fetchone():
                print(f"❌ {banco}: Tabela 'active_signals' não existe")
                conn.close()
                continue
            
            # Contar sinais
            cursor.execute("SELECT COUNT(*) FROM active_signals")
            total = cursor.fetchone()[0]
            
            print(f"✅ {banco}: {total} sinais")
            
            if total > 0:
                # Mostrar alguns detalhes
                cursor.execute("SELECT id, symbol, side, entry_price FROM active_signals LIMIT 3")
                sinais = cursor.fetchall()
                
                for sinal in sinais:
                    print(f"    ID: {sinal[0]}, Symbol: {sinal[1]}, Side: {sinal[2]}, Entry: {sinal[3]}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ {banco}: Erro - {e}")

if __name__ == "__main__":
    verificar_todos_bancos() 