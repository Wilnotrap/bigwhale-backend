#!/usr/bin/env python3
"""
Script corrigido para unificar bancos com estruturas diferentes
"""

import sqlite3
import os
import shutil
from datetime import datetime

def unificar_bancos_corrigido():
    """Unifica bancos com estruturas diferentes"""
    
    print("🔄 UNIFICANDO BANCOS (VERSÃO CORRIGIDA)")
    print("=" * 50)
    
    # Usar site.db como banco principal
    banco_principal = 'site.db'
    principal_path = os.path.join('instance', banco_principal)
    
    if not os.path.exists(principal_path):
        print(f"❌ Banco principal {banco_principal} não encontrado!")
        return
    
    print(f"🎯 Usando {banco_principal} como banco principal")
    
    # Conectar ao banco principal
    conn_principal = sqlite3.connect(principal_path)
    cursor_principal = conn_principal.cursor()
    
    # Verificar estrutura da tabela principal
    cursor_principal.execute("PRAGMA table_info(active_signals)")
    colunas_principal = [row[1] for row in cursor_principal.fetchall()]
    print(f"📊 Colunas no banco principal: {', '.join(colunas_principal)}")
    
    # Verificar sinais no banco principal
    cursor_principal.execute("SELECT COUNT(*) FROM active_signals")
    sinais_principal = cursor_principal.fetchone()[0]
    print(f"📊 Sinais no banco principal: {sinais_principal}")
    
    # Migrar sinais do site.db
    nautilus_path = os.path.join('instance', 'site.db')
    if os.path.exists(nautilus_path):
        print(f"\n🔄 Migrando sinais de site.db...")
        
        try:
            conn_nautilus = sqlite3.connect(nautilus_path)
            cursor_nautilus = conn_nautilus.cursor()
            
            # Verificar estrutura da tabela nautilus
            cursor_nautilus.execute("PRAGMA table_info(active_signals)")
            colunas_nautilus = [row[1] for row in cursor_nautilus.fetchall()]
            print(f"📊 Colunas no site.db: {', '.join(colunas_nautilus)}")
            
            # Buscar sinais
            cursor_nautilus.execute("SELECT * FROM active_signals")
            sinais = cursor_nautilus.fetchall()
            
            if not sinais:
                print(f"  ℹ️ Nenhum sinal encontrado em site.db")
            else:
                print(f"  📋 Encontrados {len(sinais)} sinais")
                
                # Migrar cada sinal
                sinais_migrados = 0
                for sinal in sinais:
                    try:
                        # Verificar se o sinal já existe (por ID)
                        cursor_principal.execute("SELECT id FROM active_signals WHERE id = ?", (sinal[0],))
                        if cursor_principal.fetchone():
                            print(f"    ⚠️ Sinal ID {sinal[0]} já existe, pulando...")
                            continue
                        
                        # Criar valores para inserção baseado na estrutura do banco principal
                        valores = list(sinal)  # Valores do nautilus
                        
                        # Adicionar valores padrão para colunas que faltam
                        while len(valores) < len(colunas_principal):
                            valores.append(None)
                        
                        # Inserir sinal
                        placeholders = ', '.join(['?' for _ in valores])
                        cursor_principal.execute(f"INSERT INTO active_signals VALUES ({placeholders})", valores)
                        sinais_migrados += 1
                        print(f"    ✅ Sinal ID {sinal[0]} migrado")
                        
                    except Exception as e:
                        print(f"    ❌ Erro ao migrar sinal ID {sinal[0]}: {e}")
                
                print(f"  📈 {sinais_migrados} sinais migrados com sucesso")
            
            conn_nautilus.close()
            
        except Exception as e:
            print(f"  ❌ Erro ao processar site.db: {e}")
    
    # Migrar sinais do site_backup.db
    backup_path = os.path.join('instance', 'site_backup.db')
    if os.path.exists(backup_path):
        print(f"\n🔄 Migrando sinais de site_backup.db...")
        
        try:
            conn_backup = sqlite3.connect(backup_path)
            cursor_backup = conn_backup.cursor()
            
            # Verificar estrutura da tabela backup
            cursor_backup.execute("PRAGMA table_info(active_signals)")
            colunas_backup = [row[1] for row in cursor_backup.fetchall()]
            print(f"📊 Colunas no site_backup.db: {', '.join(colunas_backup)}")
            
            # Buscar sinais
            cursor_backup.execute("SELECT * FROM active_signals")
            sinais = cursor_backup.fetchall()
            
            if not sinais:
                print(f"  ℹ️ Nenhum sinal encontrado em site_backup.db")
            else:
                print(f"  📋 Encontrados {len(sinais)} sinais")
                
                # Migrar cada sinal
                sinais_migrados = 0
                for sinal in sinais:
                    try:
                        # Verificar se o sinal já existe (por ID)
                        cursor_principal.execute("SELECT id FROM active_signals WHERE id = ?", (sinal[0],))
                        if cursor_principal.fetchone():
                            print(f"    ⚠️ Sinal ID {sinal[0]} já existe, pulando...")
                            continue
                        
                        # Criar valores para inserção baseado na estrutura do banco principal
                        valores = list(sinal)  # Valores do backup
                        
                        # Adicionar valores padrão para colunas que faltam
                        while len(valores) < len(colunas_principal):
                            valores.append(None)
                        
                        # Inserir sinal
                        placeholders = ', '.join(['?' for _ in valores])
                        cursor_principal.execute(f"INSERT INTO active_signals VALUES ({placeholders})", valores)
                        sinais_migrados += 1
                        print(f"    ✅ Sinal ID {sinal[0]} migrado")
                        
                    except Exception as e:
                        print(f"    ❌ Erro ao migrar sinal ID {sinal[0]}: {e}")
                
                print(f"  📈 {sinais_migrados} sinais migrados com sucesso")
            
            conn_backup.close()
            
        except Exception as e:
            print(f"  ❌ Erro ao processar site_backup.db: {e}")
    
    # Commit das mudanças
    conn_principal.commit()
    
    # Verificar resultado final
    cursor_principal.execute("SELECT COUNT(*) FROM active_signals")
    sinais_finais = cursor_principal.fetchone()[0]
    
    print(f"\n🎉 MIGRAÇÃO CONCLUÍDA!")
    print(f"📊 Sinais no banco principal: {sinais_finais}")
    
    # Fazer backup do banco principal
    backup_path = os.path.join('instance', f'site_unified_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(principal_path, backup_path)
    print(f"💾 Backup criado: {backup_path}")
    
    # Remover bancos desnecessários
    print(f"\n🗑️ Removendo bancos desnecessários...")
    bancos_para_remover = ['site.db', 'site_backup.db']
    
    for banco in bancos_para_remover:
        db_path = os.path.join('instance', banco)
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"  ✅ {banco} removido")
            except Exception as e:
                print(f"  ❌ Erro ao remover {banco}: {e}")
    
    conn_principal.close()
    
    print(f"\n✅ UNIFICAÇÃO CONCLUÍDA!")
    print(f"🎯 Agora temos apenas 1 banco: {banco_principal}")
    print(f"📊 Total de sinais: {sinais_finais}")

if __name__ == "__main__":
    unificar_bancos_corrigido() 