#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela active_signals
"""

import sqlite3
import os

def verificar_estrutura_tabela():
    """Verifica a estrutura da tabela active_signals"""
    
    try:
        print("🔍 VERIFICANDO ESTRUTURA DA TABELA ACTIVE_SIGNALS")
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
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
        if not cursor.fetchone():
            print("❌ Tabela active_signals não existe")
            conn.close()
            return
        
        print("✅ Tabela active_signals existe")
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(active_signals)")
        columns = cursor.fetchall()
        
        print(f"\n📋 ESTRUTURA DA TABELA:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM active_signals")
        count = cursor.fetchall()[0][0]
        print(f"\n📊 Total de registros: {count}")
        
        # Mostrar alguns registros
        cursor.execute("SELECT * FROM active_signals LIMIT 3")
        records = cursor.fetchall()
        
        print(f"\n📋 PRIMEIROS REGISTROS:")
        for i, record in enumerate(records, 1):
            print(f"\n   Registro {i}:")
            for j, col in enumerate(columns):
                print(f"      {col[1]}: {record[j]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_estrutura_tabela() 