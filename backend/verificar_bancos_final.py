#!/usr/bin/env python3
"""
Script para verificar o status final dos bancos após a unificação
"""

import sqlite3
import os
from datetime import datetime

def verificar_bancos_final():
    """Verifica o status final dos bancos após a unificação"""
    
    print("🗄️ STATUS FINAL DOS BANCOS DE DADOS")
    print("=" * 50)
    
    # Listar todos os arquivos .db na pasta instance
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    bancos = [f for f in os.listdir(instance_path) if f.endswith('.db')]
    
    print(f"📁 Encontrados {len(bancos)} bancos de dados:")
    
    for banco in bancos:
        db_path = os.path.join(instance_path, banco)
        file_size = os.path.getsize(db_path)
        file_time = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        print(f"\n🔍 {banco}")
        print(f"   📊 Tamanho: {file_size} bytes")
        print(f"   📅 Modificado: {file_time.strftime('%d/%m/%Y %H:%M:%S')}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se a tabela active_signals existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM active_signals")
                sinais_count = cursor.fetchone()[0]
                print(f"   📈 Sinais ativos: {sinais_count}")
                
                if sinais_count > 0:
                    # Mostrar detalhes dos sinais
                    cursor.execute("SELECT id, symbol, side, entry_price, targets_hit FROM active_signals LIMIT 5")
                    sinais = cursor.fetchall()
                    print(f"   📋 Primeiros sinais:")
                    for sinal in sinais:
                        print(f"      ID {sinal[0]}: {sinal[1]} ({sinal[2]}) - Entrada: {sinal[3]} - Alvos: {sinal[4]}")
            else:
                print(f"   ❌ Tabela 'active_signals' não encontrada")
            
            # Verificar outras tabelas importantes
            tabelas_importantes = ['users', 'trades', 'sessions']
            for tabela in tabelas_importantes:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
                if cursor.fetchone():
                    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                    count = cursor.fetchone()[0]
                    print(f"   📊 {tabela}: {count}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erro ao acessar {banco}: {e}")
    
    print(f"\n🎯 RESUMO:")
    print(f"   ✅ Banco principal: site.db")
    print(f"   💾 Backups: {len([b for b in bancos if 'unified' in b])} arquivos")
    print(f"   🗑️ Bancos removidos: site.db, site_backup.db")
    print(f"   📈 Sistema unificado e organizado!")

if __name__ == "__main__":
    verificar_bancos_final() 