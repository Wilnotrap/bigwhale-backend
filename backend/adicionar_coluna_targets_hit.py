#!/usr/bin/env python3
"""
Script para adicionar a coluna targets_hit à tabela active_signals
"""

import sqlite3
import os

def adicionar_coluna_targets_hit():
    """Adiciona a coluna targets_hit à tabela active_signals"""
    
    try:
        print("🔧 ADICIONANDO COLUNA TARGETS_HIT")
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
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(active_signals)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'targets_hit' in column_names:
            print("✅ Coluna targets_hit já existe")
            conn.close()
            return
        
        print("📝 Adicionando coluna targets_hit...")
        
        # Adicionar a coluna
        cursor.execute("ALTER TABLE active_signals ADD COLUMN targets_hit INTEGER DEFAULT 0")
        
        # Verificar se foi adicionada
        cursor.execute("PRAGMA table_info(active_signals)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'targets_hit' in column_names:
            print("✅ Coluna targets_hit adicionada com sucesso")
            
            # Atualizar valores iniciais baseado nos targets existentes
            print("🔄 Atualizando valores iniciais...")
            
            cursor.execute("SELECT id, targets FROM active_signals")
            signals = cursor.fetchall()
            
            for signal_id, targets_json in signals:
                try:
                    import json
                    targets = json.loads(targets_json)
                    # Inicialmente, nenhum alvo foi atingido
                    cursor.execute("UPDATE active_signals SET targets_hit = 0 WHERE id = ?", (signal_id,))
                except:
                    # Se não conseguir parsear JSON, definir como 0
                    cursor.execute("UPDATE active_signals SET targets_hit = 0 WHERE id = ?", (signal_id,))
            
            # Commit das alterações
            conn.commit()
            print(f"✅ {len(signals)} sinais atualizados")
            
        else:
            print("❌ Erro ao adicionar coluna")
        
        # Mostrar nova estrutura
        cursor.execute("PRAGMA table_info(active_signals)")
        columns = cursor.fetchall()
        
        print(f"\n📋 NOVA ESTRUTURA DA TABELA:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    adicionar_coluna_targets_hit() 