#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuário em produção
Verifica se o usuário tellespio93@gmail.com está no banco
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from datetime import datetime

def check_production_user():
    """Verifica o usuário tellespio93@gmail.com no banco de produção"""
    try:
        print("🔍 Verificando usuário em produção...")
        print("=" * 50)
        
        # Caminhos possíveis do banco
        possible_db_paths = [
            os.path.join('backend', 'instance', 'site.db'),
            os.path.join('instance', 'site.db'),
            'site.db',
            os.path.join('backend', 'trading_signals.db'),
            'trading_signals.db'
        ]
        
        db_path = None
        for path in possible_db_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            print("❌ Banco de dados não encontrado!")
            print("Caminhos verificados:")
            for path in possible_db_paths:
                print(f"   - {path}")
            return False
        
        print(f"📁 Usando banco: {db_path}")
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Tabela 'users' não encontrada!")
            return False
        
        # Buscar o usuário específico
        email = 'tellespio93@gmail.com'
        print(f"🔍 Procurando usuário: {email}")
        
        cursor.execute("""
            SELECT id, full_name, email, is_active, is_admin, 
                   operational_balance, operational_balance_usd,
                   bitget_api_key_encrypted, bitget_api_secret_encrypted, bitget_passphrase_encrypted,
                   created_at, last_login, nautilus_active, nautilus_user_id
            FROM users 
            WHERE email = ?
        """, (email,))
        
        user = cursor.fetchone()
        
        if user:
            print("✅ Usuário encontrado!")
            print(f"   ID: {user[0]}")
            print(f"   Nome: {user[1]}")
            print(f"   Email: {user[2]}")
            print(f"   Ativo: {'Sim' if user[3] else 'Não'}")
            print(f"   Admin: {'Sim' if user[4] else 'Não'}")
            print(f"   Saldo BRL: R$ {user[5] or 0:.2f}")
            print(f"   Saldo USD: $ {user[6] or 0:.2f}")
            print(f"   API Key: {'Configurada' if user[7] else 'Não configurada'}")
            print(f"   API Secret: {'Configurada' if user[8] else 'Não configurada'}")
            print(f"   Passphrase: {'Configurada' if user[9] else 'Não configurada'}")
            print(f"   Criado em: {user[10]}")
            print(f"   Último login: {user[11] or 'Nunca'}")
            print(f"   Nautilus ativo: {'Sim' if user[12] else 'Não'}")
            print(f"   Nautilus ID: {user[13] or 'Não definido'}")
            
            user_id = user[0]
            
        else:
            print("❌ Usuário não encontrado!")
            
            # Verificar se existe algum usuário com email similar
            cursor.execute("SELECT email FROM users WHERE email LIKE ?", (f'%{email.split("@")[0]}%',))
            similar_users = cursor.fetchall()
            
            if similar_users:
                print("\n🔍 Usuários com email similar encontrados:")
                for similar in similar_users:
                    print(f"   - {similar[0]}")
            
            return False
        
        # Verificar códigos de convite
        print(f"\n🎫 Verificando códigos de convite...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invite_codes'")
        if cursor.fetchone():
            cursor.execute("""
                SELECT code, max_uses, used_count, is_active, created_at, last_used_at
                FROM invite_codes 
                WHERE code = ?
            """, ('Bigwhale81#',))
            
            invite = cursor.fetchone()
            if invite:
                print(f"✅ Código de convite encontrado:")
                print(f"   Código: {invite[0]}")
                print(f"   Máximo usos: {invite[1] or 'Ilimitado'}")
                print(f"   Usos: {invite[2]}")
                print(f"   Ativo: {'Sim' if invite[3] else 'Não'}")
                print(f"   Criado em: {invite[4]}")
                print(f"   Último uso: {invite[5] or 'Nunca usado'}")
            else:
                print("❌ Código de convite 'Bigwhale81#' não encontrado!")
        else:
            print("⚠️  Tabela 'invite_codes' não existe")
        
        # Verificar logs de erro (se existir tabela)
        print(f"\n📋 Verificando possíveis erros...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tabelas disponíveis: {', '.join(tables)}")
        
        # Verificar se há registros de sessão
        if 'user_sessions' in tables:
            cursor.execute("""
                SELECT session_token, created_at, last_activity, is_active
                FROM user_sessions 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 5
            """, (user_id,))
            
            sessions = cursor.fetchall()
            if sessions:
                print(f"\n🔐 Últimas sessões do usuário:")
                for session in sessions:
                    status = "Ativa" if session[3] else "Inativa"
                    print(f"   Token: {session[0][:20]}... - {session[1]} - {status}")
            else:
                print("\n⚠️  Nenhuma sessão encontrada para o usuário")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("🎯 Diagnóstico:")
        
        if user:
            api_configured = bool(user[7] and user[8] and user[9])
            if not api_configured:
                print("⚠️  PROBLEMA: Credenciais da API não estão configuradas")
                print("💡 SOLUÇÃO: Usuário precisa configurar API Key, Secret e Passphrase")
            
            if not user[3]:  # is_active
                print("⚠️  PROBLEMA: Usuário está inativo")
                print("💡 SOLUÇÃO: Ativar usuário no sistema")
            
            if user[12] and not user[13]:  # nautilus_active mas sem nautilus_user_id
                print("⚠️  PROBLEMA: Nautilus ativo mas sem ID do usuário")
                print("💡 SOLUÇÃO: Verificar integração com Nautilus")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔍 Verificação de Usuário em Produção")
    print("Email: tellespio93@gmail.com")
    print("Código: Bigwhale81#")
    
    success = check_production_user()
    
    if success:
        print("\n✅ Verificação concluída!")
    else:
        print("\n❌ Problemas encontrados na verificação!")