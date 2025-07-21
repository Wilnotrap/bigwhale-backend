#!/usr/bin/env python3
"""
Script final para corrigir todos os problemas de datetime no banco
"""

import sqlite3
import os
from datetime import datetime

def corrigir_datetime_final():
    """Corrige definitivamente todos os problemas de datetime"""
    
    try:
        print("🔧 CORREÇÃO FINAL DE DATETIME")
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
        
        # Buscar todos os sinais com problemas de datetime
        cursor.execute("""
            SELECT id, created_at, updated_at
            FROM active_signals 
            WHERE created_at IS NOT NULL OR updated_at IS NOT NULL
        """)
        
        signals = cursor.fetchall()
        print(f"📊 Encontrados {len(signals)} sinais para verificar")
        
        # Corrigir cada sinal
        for signal in signals:
            signal_id, created_at, updated_at = signal
            
            try:
                # Corrigir created_at
                if created_at:
                    if isinstance(created_at, str):
                        # Tentar converter string para datetime
                        try:
                            # Remover timezone se existir
                            if created_at.endswith('+00:00'):
                                created_at = created_at[:-6]
                            elif created_at.endswith('Z'):
                                created_at = created_at[:-1]
                            
                            # Tentar diferentes formatos
                            formats = [
                                '%Y-%m-%d %H:%M:%S',
                                '%Y-%m-%d %H:%M:%S.%f',
                                '%Y-%m-%dT%H:%M:%S',
                                '%Y-%m-%dT%H:%M:%S.%f'
                            ]
                            
                            parsed_created = None
                            for fmt in formats:
                                try:
                                    parsed_created = datetime.strptime(created_at, fmt)
                                    break
                                except ValueError:
                                    continue
                            
                            if parsed_created:
                                cursor.execute(
                                    "UPDATE active_signals SET created_at = ? WHERE id = ?",
                                    (parsed_created.isoformat(), signal_id)
                                )
                                print(f"✅ Corrigido created_at para sinal {signal_id}")
                            else:
                                # Se não conseguir converter, usar datetime atual
                                cursor.execute(
                                    "UPDATE active_signals SET created_at = ? WHERE id = ?",
                                    (datetime.now().isoformat(), signal_id)
                                )
                                print(f"⚠️ Definido created_at atual para sinal {signal_id}")
                        except Exception as e:
                            print(f"❌ Erro ao corrigir created_at do sinal {signal_id}: {e}")
                
                # Corrigir updated_at
                if updated_at:
                    if isinstance(updated_at, str):
                        try:
                            # Remover timezone se existir
                            if updated_at.endswith('+00:00'):
                                updated_at = updated_at[:-6]
                            elif updated_at.endswith('Z'):
                                updated_at = updated_at[:-1]
                            
                            # Tentar diferentes formatos
                            formats = [
                                '%Y-%m-%d %H:%M:%S',
                                '%Y-%m-%d %H:%M:%S.%f',
                                '%Y-%m-%dT%H:%M:%S',
                                '%Y-%m-%dT%H:%M:%S.%f'
                            ]
                            
                            parsed_updated = None
                            for fmt in formats:
                                try:
                                    parsed_updated = datetime.strptime(updated_at, fmt)
                                    break
                                except ValueError:
                                    continue
                            
                            if parsed_updated:
                                cursor.execute(
                                    "UPDATE active_signals SET updated_at = ? WHERE id = ?",
                                    (parsed_updated.isoformat(), signal_id)
                                )
                                print(f"✅ Corrigido updated_at para sinal {signal_id}")
                            else:
                                # Se não conseguir converter, usar datetime atual
                                cursor.execute(
                                    "UPDATE active_signals SET updated_at = ? WHERE id = ?",
                                    (datetime.now().isoformat(), signal_id)
                                )
                                print(f"⚠️ Definido updated_at atual para sinal {signal_id}")
                        except Exception as e:
                            print(f"❌ Erro ao corrigir updated_at do sinal {signal_id}: {e}")
                

                
            except Exception as e:
                print(f"❌ Erro geral ao processar sinal {signal_id}: {e}")
                continue
        
        # Commit das alterações
        conn.commit()
        print("✅ Alterações salvas no banco")
        
        # Verificar se ainda há problemas
        cursor.execute("""
            SELECT COUNT(*) FROM active_signals 
            WHERE created_at IS NULL OR updated_at IS NULL
        """)
        
        null_count = cursor.fetchone()[0]
        print(f"📊 Sinais com campos NULL: {null_count}")
        
        # Definir valores padrão para campos NULL
        if null_count > 0:
            cursor.execute("""
                UPDATE active_signals 
                SET created_at = ?, updated_at = ? 
                WHERE created_at IS NULL OR updated_at IS NULL
            """, (datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            print("✅ Campos NULL corrigidos")
        
        conn.close()
        print("🎉 Correção de datetime concluída!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    corrigir_datetime_final() 