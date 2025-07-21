#!/usr/bin/env python3
"""
Script para verificar a estrutura completa do banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

def verificar_banco_completo():
    """Verifica a estrutura completa do banco de dados"""
    
    try:
        # Configurar conexão direta com o banco
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado em: {db_path}")
            return
            
        print(f"✅ Banco encontrado: {db_path}")
        
        engine = create_engine(f'sqlite:///{db_path}')
        
        with engine.connect() as conn:
            # Listar todas as tabelas
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
                ORDER BY name
            """))
            
            tabelas = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
            print("-" * 40)
            
            for tabela in tabelas:
                # Contar registros em cada tabela
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                    count = count_result.fetchone()[0]
                    print(f"• {tabela}: {count} registros")
                except Exception as e:
                    print(f"• {tabela}: Erro ao contar - {e}")
            
            # Verificar especificamente a tabela active_signals
            if 'active_signals' in tabelas:
                print(f"\n🔍 Detalhes da tabela 'active_signals':")
                print("-" * 40)
                
                # Estrutura da tabela
                result = conn.execute(text("PRAGMA table_info(active_signals)"))
                colunas = result.fetchall()
                
                print("Colunas:")
                for col in colunas:
                    print(f"  • {col[1]} ({col[2]})")
                
                # Alguns registros de exemplo
                result = conn.execute(text("""
                    SELECT * FROM active_signals 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """))
                registros = result.fetchall()
                
                if registros:
                    print(f"\nÚltimos 3 registros:")
                    for reg in registros:
                        print(f"  {reg}")
                else:
                    print("\nNenhum registro encontrado")
                    
            else:
                print(f"\n⚠️  Tabela 'active_signals' não existe!")
                print("Isso pode indicar que:")
                print("1. O banco não foi inicializado corretamente")
                print("2. A sincronização com Nautilus não está funcionando")
                print("3. Há um problema na criação das tabelas")
                
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_banco_completo() 