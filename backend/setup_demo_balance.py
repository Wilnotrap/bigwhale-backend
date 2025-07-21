#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar saldo da conta demo
"""

import sqlite3
import os

def setup_demo_balance():
    """Configura saldo de $600 para a conta demo"""
    try:
        # Caminho do banco
        db_path = os.path.join('backend', 'instance', 'site.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado em: {db_path}")
            return False
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se usuário existe
        cursor.execute("SELECT id, full_name FROM users WHERE email = ?", ('financeiro@lexxusadm.com.br',))
        user = cursor.fetchone()
        
        if not user:
            print("❌ Usuário demo não encontrado!")
            return False
        
        user_id = user[0]
        user_name = user[1]
        
        print(f"👤 Configurando saldo para: {user_name} (ID: {user_id})")
        
        # Atualizar saldo operacional
        cursor.execute("""
            UPDATE users 
            SET operational_balance = ?, 
                operational_balance_usd = ?,
                nautilus_active = 1
            WHERE id = ?
        """, (600.0, 600.0, user_id))
        
        # Salvar alterações
        conn.commit()
        
        # Verificar se foi atualizado
        cursor.execute("SELECT operational_balance, operational_balance_usd, nautilus_active FROM users WHERE id = ?", (user_id,))
        balance_data = cursor.fetchone()
        
        if balance_data:
            print(f"✅ Saldo configurado:")
            print(f"   💰 Saldo BRL: R$ {balance_data[0]:.2f}")
            print(f"   💵 Saldo USD: $ {balance_data[1]:.2f}")
            print(f"   🤖 Nautilus Ativo: {'Sim' if balance_data[2] else 'Não'}")
        
        conn.close()
        
        print("\n🎉 Saldo da conta demo configurado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    print("💰 Configurando saldo da conta demo...")
    success = setup_demo_balance()
    
    if success:
        print("\n✅ Processo concluído!")
    else:
        print("\n❌ Processo falhou!")