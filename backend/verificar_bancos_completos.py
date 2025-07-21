#!/usr/bin/env python3
"""
Script para verificar todos os bancos de dados e suas tabelas
"""

import sqlite3
import os

def verificar_bancos_completos():
    """Verifica todos os bancos de dados e suas tabelas"""
    
    print("🗄️ VERIFICANDO TODOS OS BANCOS DE DADOS")
    print("=" * 60)
    
    # Listar todos os arquivos .db na pasta instance
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    bancos = [f for f in os.listdir(instance_path) if f.endswith('.db')]
    
    print(f"📁 Encontrados {len(bancos)} bancos de dados:")
    
    for banco in bancos:
        db_path = os.path.join(instance_path, banco)
        file_size = os.path.getsize(db_path)
        
        print(f"\n🔍 {banco} ({file_size} bytes)")
        print("-" * 40)
        
        try:
            # Conectar ao banco
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()
            
            print(f"📊 Tabelas encontradas: {len(tabelas)}")
            
            for tabela in tabelas:
                nome_tabela = tabela[0]
                
                # Contar registros em cada tabela
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
                    count = cursor.fetchone()[0]
                    print(f"  • {nome_tabela}: {count} registros")
                    
                    # Se for active_signals, mostrar alguns detalhes
                    if nome_tabela == 'active_signals' and count > 0:
                        cursor.execute(f"SELECT id, symbol, side FROM {nome_tabela} LIMIT 3")
                        sinais = cursor.fetchall()
                        for sinal in sinais:
                            print(f"    - ID: {sinal[0]}, Symbol: {sinal[1]}, Side: {sinal[2]}")
                            
                except Exception as e:
                    print(f"  • {nome_tabela}: Erro ao contar - {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao acessar {banco}: {e}")

if __name__ == "__main__":
    verificar_bancos_completos() 