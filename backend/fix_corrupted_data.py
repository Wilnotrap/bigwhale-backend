#!/usr/bin/env python3
"""
Script para corrigir dados corrompidos no banco de dados
Remove registros com datetime inválido e corrige problemas
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def fix_corrupted_data():
    """Corrige dados corrompidos no banco de dados"""
    
    print("🔧 CORREÇÃO DE DADOS CORROMPIDOS")
    print("=" * 50)
    
    # Caminho do banco
    db_path = Path("backend/instance/site.db")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Tabelas encontradas: {tables}")
        
        # 2. Corrigir tabela active_signals
        if 'active_signals' in tables:
            print("\n🔧 Corrigindo tabela active_signals...")
            
            # Verificar registros com datetime inválido
            cursor.execute("""
                SELECT id, created_at, updated_at, completed_at 
                FROM active_signals 
                WHERE created_at IS NOT NULL OR updated_at IS NOT NULL OR completed_at IS NOT NULL
            """)
            
            records = cursor.fetchall()
            print(f"📝 Verificando {len(records)} registros...")
            
            fixed_count = 0
            for record in records:
                record_id, created_at, updated_at, completed_at = record
                
                needs_fix = False
                
                # Verificar created_at
                if created_at and not is_valid_datetime(created_at):
                    print(f"   ❌ Registro {record_id}: created_at inválido '{created_at}'")
                    needs_fix = True
                
                # Verificar updated_at
                if updated_at and not is_valid_datetime(updated_at):
                    print(f"   ❌ Registro {record_id}: updated_at inválido '{updated_at}'")
                    needs_fix = True
                
                # Verificar completed_at
                if completed_at and not is_valid_datetime(completed_at):
                    print(f"   ❌ Registro {record_id}: completed_at inválido '{completed_at}'")
                    needs_fix = True
                
                if needs_fix:
                    # Corrigir registros com datetime inválido
                    cursor.execute("""
                        UPDATE active_signals 
                        SET created_at = ?, updated_at = ?, completed_at = ?
                        WHERE id = ?
                    """, (
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        None,  # completed_at sempre None para registros ativos
                        record_id
                    ))
                    fixed_count += 1
            
            print(f"✅ {fixed_count} registros corrigidos")
        
        # 3. Verificar e corrigir targets_json
        print("\n🔧 Verificando targets_json...")
        cursor.execute("SELECT id, targets_json FROM active_signals WHERE targets_json IS NOT NULL")
        
        targets_records = cursor.fetchall()
        targets_fixed = 0
        
        for record in targets_records:
            record_id, targets_json = record
            
            try:
                # Tentar fazer parse do JSON
                import json
                json.loads(targets_json)
            except:
                print(f"   ❌ Registro {record_id}: targets_json inválido")
                # Corrigir com array vazio
                cursor.execute("""
                    UPDATE active_signals 
                    SET targets_json = '[]'
                    WHERE id = ?
                """, (record_id,))
                targets_fixed += 1
        
        print(f"✅ {targets_fixed} targets_json corrigidos")
        
        # 4. Verificar integridade geral
        print("\n🔍 Verificando integridade geral...")
        
        # Contar registros válidos
        cursor.execute("SELECT COUNT(*) FROM active_signals WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM active_signals WHERE status = 'completed'")
        completed_count = cursor.fetchone()[0]
        
        print(f"📊 Sinais ativos: {active_count}")
        print(f"📊 Sinais completados: {completed_count}")
        
        # 5. Commit das alterações
        conn.commit()
        conn.close()
        
        print("\n✅ Correção concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante correção: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def is_valid_datetime(dt_string):
    """Verifica se uma string é um datetime válido"""
    if not dt_string:
        return True  # None é válido
    
    try:
        # Tentar diferentes formatos
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(dt_string, fmt)
                return True
            except ValueError:
                continue
        
        # Tentar ISO format
        datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return True
        
    except:
        return False

if __name__ == "__main__":
    fix_corrupted_data() 