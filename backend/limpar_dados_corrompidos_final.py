#!/usr/bin/env python3
"""
Script para limpar definitivamente os dados corrompidos do banco
"""

import sqlite3
import os
from datetime import datetime

def limpar_dados_corrompidos_final():
    """Limpa definitivamente os dados corrompidos do banco"""
    
    try:
        print("🧹 LIMPANDO DADOS CORROMPIDOS DEFINITIVAMENTE")
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
        
        # Limpar dados corrompidos na tabela active_signals
        print("🔧 Limpando dados corrompidos na tabela active_signals...")
        
        # Atualizar campos de datetime corrompidos
        cursor.execute("""
            UPDATE active_signals 
            SET created_at = NULL, updated_at = NULL, completed_at = NULL
            WHERE created_at LIKE '%T%' OR updated_at LIKE '%T%' OR completed_at LIKE '%T%'
        """)
        
        rows_updated = cursor.rowcount
        print(f"✅ {rows_updated} registros com datetime corrompido foram limpos")
        
        # Verificar se há outros dados corrompidos
        cursor.execute("SELECT COUNT(*) FROM active_signals")
        total_signals = cursor.fetchone()[0]
        print(f"📊 Total de sinais no banco: {total_signals}")
        
        # Mostrar alguns sinais para verificar
        cursor.execute("SELECT id, symbol, side, entry_price, targets_json, targets_hit FROM active_signals LIMIT 5")
        signals = cursor.fetchall()
        
        print("\n📋 PRIMEIROS SINAIS NO BANCO:")
        for signal in signals:
            signal_id, symbol, side, entry_price, targets_json, targets_hit = signal
            print(f"   ID: {signal_id}, Símbolo: {symbol}, Lado: {side}, Preço: {entry_price}, Alvos: {targets_hit}")
        
        # Commit das alterações
        conn.commit()
        print("\n✅ Dados corrompidos limpos com sucesso!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados corrompidos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    limpar_dados_corrompidos_final() 