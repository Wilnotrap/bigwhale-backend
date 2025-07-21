#!/usr/bin/env python3
"""
Script para resolver definitivamente o problema de datetime
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def fix_datetime_issue():
    """Resolve o problema de datetime de forma definitiva"""
    
    print("🔧 CORREÇÃO DEFINITIVA DO PROBLEMA DE DATETIME")
    print("=" * 60)
    
    # Caminho do banco
    db_path = Path("instance/site.db")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado")
        return False
    
    try:
        # Fazer backup do banco
        backup_path = Path("instance/site_backup.db")
        if db_path.exists():
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Backup criado: {backup_path}")
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando tabela active_signals...")
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
        if not cursor.fetchone():
            print("❌ Tabela active_signals não existe")
            conn.close()
            return False
        
        # Buscar todos os registros com problemas de datetime
        cursor.execute("""
            SELECT id, created_at, updated_at, completed_at, targets_json, symbol, side, entry_price
            FROM active_signals
        """)
        
        records = cursor.fetchall()
        print(f"📊 Encontrados {len(records)} registros")
        
        fixed_count = 0
        corrupted_count = 0
        
        for record in records:
            record_id, created_at, updated_at, completed_at, targets_json, symbol, side, entry_price = record
            
            needs_fix = False
            new_created_at = None
            new_updated_at = None
            new_completed_at = None
            
            # Verificar e corrigir created_at
            if created_at:
                try:
                    # Tentar diferentes formatos
                    if isinstance(created_at, str):
                        # Se é string, tentar converter
                        try:
                            datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            new_created_at = created_at
                        except:
                            # Se falhar, usar datetime atual
                            new_created_at = datetime.now().isoformat()
                            needs_fix = True
                    else:
                        # Se não é string, usar datetime atual
                        new_created_at = datetime.now().isoformat()
                        needs_fix = True
                except:
                    new_created_at = datetime.now().isoformat()
                    needs_fix = True
            
            # Verificar e corrigir updated_at
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        try:
                            datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                            new_updated_at = updated_at
                        except:
                            new_updated_at = datetime.now().isoformat()
                            needs_fix = True
                    else:
                        new_updated_at = datetime.now().isoformat()
                        needs_fix = True
                except:
                    new_updated_at = datetime.now().isoformat()
                    needs_fix = True
            
            # Verificar e corrigir completed_at
            if completed_at:
                try:
                    if isinstance(completed_at, str):
                        try:
                            datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                            new_completed_at = completed_at
                        except:
                            new_completed_at = None  # Se é corrompido, deixar como None
                            needs_fix = True
                    else:
                        new_completed_at = None
                        needs_fix = True
                except:
                    new_completed_at = None
                    needs_fix = True
            
            # Verificar targets_json
            if targets_json:
                try:
                    import json
                    json.loads(targets_json)
                except:
                    # Se targets_json é inválido, corrigir
                    targets_json = '[]'
                    needs_fix = True
            
            if needs_fix:
                print(f"🔧 Corrigindo registro {record_id}: {symbol} {side}")
                
                # Atualizar registro
                cursor.execute("""
                    UPDATE active_signals 
                    SET created_at = ?, updated_at = ?, completed_at = ?, targets_json = ?
                    WHERE id = ?
                """, (new_created_at, new_updated_at, new_completed_at, targets_json, record_id))
                
                fixed_count += 1
            else:
                print(f"✅ Registro {record_id}: {symbol} {side} - OK")
        
        # Salvar alterações
        conn.commit()
        
        print(f"\n📊 RESUMO:")
        print(f"✅ {fixed_count} registros corrigidos")
        print(f"✅ {len(records) - fixed_count} registros já estavam OK")
        
        # Verificar se ainda há problemas
        print("\n🔍 Verificação final...")
        
        cursor.execute("SELECT COUNT(*) FROM active_signals")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM active_signals WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        
        print(f"📊 Total de sinais: {total_count}")
        print(f"📊 Sinais ativos: {active_count}")
        
        conn.close()
        
        print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ O sistema de monitoramento agora deve funcionar corretamente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    fix_datetime_issue() 