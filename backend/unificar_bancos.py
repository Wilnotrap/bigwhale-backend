#!/usr/bin/env python3
"""
Script para unificar todos os bancos em um só
"""

import sqlite3
import os
import shutil
from datetime import datetime

def unificar_bancos():
    """Unifica todos os bancos em um só"""
    
    print("🔄 UNIFICANDO BANCOS DE DADOS")
    print("=" * 50)
    
    # Bancos existentes
    bancos = {
        'site.db': 'Banco principal',
        'site.db': 'Banco principal',
        'site_backup.db': 'Banco de backup'
    }
    
    # Verificar quais bancos existem
    bancos_existentes = {}
    for banco, descricao in bancos.items():
        db_path = os.path.join('instance', banco)
        if os.path.exists(db_path):
            bancos_existentes[banco] = descricao
            print(f"✅ {banco}: {descricao}")
        else:
            print(f"❌ {banco}: Não encontrado")
    
    if not bancos_existentes:
        print("❌ Nenhum banco encontrado!")
        return
    
    # Usar site.db como banco principal
    banco_principal = 'site.db'
    if banco_principal not in bancos_existentes:
        print(f"❌ Banco principal {banco_principal} não encontrado!")
        return
    
    print(f"\n🎯 Usando {banco_principal} como banco principal")
    
    # Conectar ao banco principal
    principal_path = os.path.join('instance', banco_principal)
    conn_principal = sqlite3.connect(principal_path)
    cursor_principal = conn_principal.cursor()
    
    # Verificar sinais no banco principal
    cursor_principal.execute("SELECT COUNT(*) FROM active_signals")
    sinais_principal = cursor_principal.fetchone()[0]
    print(f"📊 Sinais no banco principal: {sinais_principal}")
    
    # Migrar sinais dos outros bancos
    sinais_migrados = 0
    
    for banco, descricao in bancos_existentes.items():
        if banco == banco_principal:
            continue
            
        db_path = os.path.join('instance', banco)
        print(f"\n🔄 Migrando sinais de {banco}...")
        
        try:
            conn_secundario = sqlite3.connect(db_path)
            cursor_secundario = conn_secundario.cursor()
            
            # Verificar se a tabela existe
            cursor_secundario.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
            if not cursor_secundario.fetchone():
                print(f"  ⚠️ Tabela active_signals não existe em {banco}")
                continue
            
            # Buscar sinais
            cursor_secundario.execute("SELECT * FROM active_signals")
            sinais = cursor_secundario.fetchall()
            
            if not sinais:
                print(f"  ℹ️ Nenhum sinal encontrado em {banco}")
                continue
            
            print(f"  📋 Encontrados {len(sinais)} sinais")
            
            # Obter estrutura da tabela
            cursor_secundario.execute("PRAGMA table_info(active_signals)")
            colunas = [row[1] for row in cursor_secundario.fetchall()]
            print(f"  📊 Colunas: {', '.join(colunas)}")
            
            # Migrar cada sinal
            for sinal in sinais:
                try:
                    # Verificar se o sinal já existe (por ID)
                    cursor_principal.execute("SELECT id FROM active_signals WHERE id = ?", (sinal[0],))
                    if cursor_principal.fetchone():
                        print(f"    ⚠️ Sinal ID {sinal[0]} já existe, pulando...")
                        continue
                    
                    # Inserir sinal
                    placeholders = ', '.join(['?' for _ in sinal])
                    cursor_principal.execute(f"INSERT INTO active_signals VALUES ({placeholders})", sinal)
                    sinais_migrados += 1
                    print(f"    ✅ Sinal ID {sinal[0]} migrado")
                    
                except Exception as e:
                    print(f"    ❌ Erro ao migrar sinal ID {sinal[0]}: {e}")
            
            conn_secundario.close()
            
        except Exception as e:
            print(f"  ❌ Erro ao processar {banco}: {e}")
    
    # Commit das mudanças
    conn_principal.commit()
    
    # Verificar resultado final
    cursor_principal.execute("SELECT COUNT(*) FROM active_signals")
    sinais_finais = cursor_principal.fetchone()[0]
    
    print(f"\n🎉 MIGRAÇÃO CONCLUÍDA!")
    print(f"📊 Sinais no banco principal: {sinais_finais}")
    print(f"📈 Sinais migrados: {sinais_migrados}")
    
    # Fazer backup do banco principal
    backup_path = os.path.join('instance', f'site_unified_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(principal_path, backup_path)
    print(f"💾 Backup criado: {backup_path}")
    
    # Remover bancos desnecessários
    print(f"\n🗑️ Removendo bancos desnecessários...")
    for banco in bancos_existentes:
        if banco != banco_principal:
            db_path = os.path.join('instance', banco)
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
    unificar_bancos() 