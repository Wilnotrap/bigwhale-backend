#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar estrutura do banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3

def check_database_structure():
    """Verifica a estrutura do banco de dados"""
    try:
        print("🔍 Verificando estrutura do banco...")
        print("=" * 50)
        
        db_path = os.path.join('backend', 'instance', 'site.db')
        if not os.path.exists(db_path):
            print("❌ Banco de dados não encontrado!")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        print("📋 TABELAS NO BANCO:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Tabela: {table_name}")
            
            # Obter estrutura da tabela
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   Colunas:")
            for col in columns:
                col_id, name, type_, not_null, default, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                primary = "PRIMARY KEY" if pk else ""
                default_val = f"DEFAULT {default}" if default else ""
                print(f"     {name} ({type_}) {nullable} {primary} {default_val}".strip())
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Registros: {count}")
        
        # Verificar especificamente a tabela invite_codes
        print(f"\n🎫 VERIFICANDO CÓDIGOS DE CONVITE:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invite_codes'")
        if cursor.fetchone():
            print("✅ Tabela invite_codes existe")
            
            # Listar todos os códigos
            cursor.execute("SELECT * FROM invite_codes")
            codes = cursor.fetchall()
            
            if codes:
                print("📋 Códigos encontrados:")
                for code in codes:
                    print(f"   {code}")
            else:
                print("❌ Nenhum código encontrado")
        else:
            print("❌ Tabela invite_codes não existe")
        
        # Verificar usuários específicos
        print(f"\n👤 VERIFICANDO USUÁRIOS ESPECÍFICOS:")
        
        # Procurar por tellespio
        cursor.execute("SELECT * FROM users WHERE email LIKE ?", ('%tellespio%',))
        telles_users = cursor.fetchall()
        
        if telles_users:
            print("✅ Usuários com 'tellespio' encontrados:")
            for user in telles_users:
                print(f"   {user}")
        else:
            print("❌ Nenhum usuário com 'tellespio' encontrado")
        
        # Procurar por gmail.com
        cursor.execute("SELECT email FROM users WHERE email LIKE ?", ('%gmail.com%',))
        gmail_users = cursor.fetchall()
        
        if gmail_users:
            print("📧 Usuários com Gmail:")
            for user in gmail_users:
                print(f"   {user[0]}")
        else:
            print("❌ Nenhum usuário com Gmail encontrado")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_database_structure()
    
    if success:
        print("\n✅ Verificação concluída!")
    else:
        print("\n❌ Erro na verificação!")