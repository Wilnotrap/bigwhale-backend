#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar todos os usuários e códigos de convite
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from datetime import datetime

def list_all_users():
    """Lista todos os usuários e códigos de convite"""
    try:
        print("📋 Listando todos os usuários e códigos...")
        print("=" * 60)
        
        # Encontrar banco
        db_path = os.path.join('backend', 'instance', 'site.db')
        if not os.path.exists(db_path):
            print("❌ Banco de dados não encontrado!")
            return False
        
        print(f"📁 Banco: {db_path}")
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todos os usuários
        print("\n👥 USUÁRIOS CADASTRADOS:")
        print("-" * 60)
        
        cursor.execute("""
            SELECT id, full_name, email, is_active, is_admin, 
                   operational_balance_usd, created_at, last_login,
                   bitget_api_key_encrypted, nautilus_active
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        
        if users:
            for i, user in enumerate(users, 1):
                status = "🟢 Ativo" if user[3] else "🔴 Inativo"
                admin = "👑 Admin" if user[4] else "👤 User"
                api_config = "🔑 API OK" if user[8] else "⚠️  Sem API"
                nautilus = "🤖 Nautilus" if user[9] else "❌ Sem Nautilus"
                
                print(f"{i:2d}. {user[1]} ({user[2]})")
                print(f"    ID: {user[0]} | {status} | {admin} | {api_config} | {nautilus}")
                print(f"    Saldo: ${user[5] or 0:.2f} | Criado: {user[6]} | Login: {user[7] or 'Nunca'}")
                print()
        else:
            print("❌ Nenhum usuário encontrado!")
        
        # Listar códigos de convite
        print("\n🎫 CÓDIGOS DE CONVITE:")
        print("-" * 60)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invite_codes'")
        if cursor.fetchone():
            cursor.execute("""
                SELECT code, max_uses, used_count, is_active, created_at, last_used_at
                FROM invite_codes 
                ORDER BY created_at DESC
            """)
            
            invites = cursor.fetchall()
            
            if invites:
                for i, invite in enumerate(invites, 1):
                    status = "🟢 Ativo" if invite[3] else "🔴 Inativo"
                    uses = f"{invite[2]}/{invite[1] or '∞'}"
                    
                    print(f"{i:2d}. {invite[0]}")
                    print(f"    {status} | Usos: {uses} | Criado: {invite[4]} | Último uso: {invite[5] or 'Nunca'}")
                    print()
            else:
                print("❌ Nenhum código de convite encontrado!")
        else:
            print("⚠️  Tabela 'invite_codes' não existe")
        
        # Verificar se existe o código específico
        print(f"\n🔍 VERIFICANDO CÓDIGO 'Bigwhale81#':")
        print("-" * 60)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invite_codes'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM invite_codes WHERE code = ?", ('Bigwhale81#',))
            specific_invite = cursor.fetchone()
            
            if specific_invite:
                print("✅ Código encontrado!")
                print(f"   Código: {specific_invite[1]}")
                print(f"   Máximo usos: {specific_invite[2] or 'Ilimitado'}")
                print(f"   Usos atuais: {specific_invite[3]}")
                print(f"   Ativo: {'Sim' if specific_invite[4] else 'Não'}")
            else:
                print("❌ Código 'Bigwhale81#' não encontrado!")
                
                # Listar códigos similares
                cursor.execute("SELECT code FROM invite_codes WHERE code LIKE ?", ('%Bigwhale%',))
                similar = cursor.fetchall()
                if similar:
                    print("🔍 Códigos similares encontrados:")
                    for code in similar:
                        print(f"   - {code[0]}")
        
        # Verificar usuários com email similar
        print(f"\n🔍 VERIFICANDO EMAILS SIMILARES A 'tellespio93@gmail.com':")
        print("-" * 60)
        
        cursor.execute("SELECT email FROM users WHERE email LIKE ? OR email LIKE ?", 
                      ('%tellespio%', '%telles%'))
        similar_emails = cursor.fetchall()
        
        if similar_emails:
            print("✅ Emails similares encontrados:")
            for email in similar_emails:
                print(f"   - {email[0]}")
        else:
            print("❌ Nenhum email similar encontrado")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO:")
        print(f"   👥 Total de usuários: {len(users) if users else 0}")
        print(f"   🎫 Total de códigos: {len(invites) if 'invites' in locals() and invites else 0}")
        print(f"   🔍 Usuário procurado: tellespio93@gmail.com - {'❌ NÃO ENCONTRADO' if not any(u[2] == 'tellespio93@gmail.com' for u in users) else '✅ ENCONTRADO'}")
        print(f"   🎫 Código procurado: Bigwhale81# - {'❌ NÃO ENCONTRADO' if 'specific_invite' in locals() and not specific_invite else '✅ ENCONTRADO' if 'specific_invite' in locals() else '❓ TABELA NÃO EXISTE'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = list_all_users()
    
    if success:
        print("\n✅ Listagem concluída!")
    else:
        print("\n❌ Erro na listagem!")