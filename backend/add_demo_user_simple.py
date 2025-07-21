#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para adicionar usuário demo
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def add_demo_user():
    """Adiciona usuário demo diretamente no banco SQLite"""
    try:
        # Caminho do banco
        db_path = os.path.join('backend', 'instance', 'site.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado em: {db_path}")
            return False
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se usuário já existe
        cursor.execute("SELECT id FROM users WHERE email = ?", ('financeiro@lexxusadm.com.br',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Atualizar usuário existente
            password_hash = generate_password_hash('FinanceiroDemo2025@')
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, full_name = ?, is_admin = ?, is_active = ?
                WHERE email = ?
            """, (password_hash, 'Conta Demo Financeiro', 0, 1, 'financeiro@lexxusadm.com.br'))
            print("✅ Usuário financeiro@lexxusadm.com.br atualizado")
        else:
            # Criar novo usuário
            password_hash = generate_password_hash('FinanceiroDemo2025@')
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash, is_active, is_admin, nautilus_active, operational_balance, operational_balance_usd, commission_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('Conta Demo Financeiro', 'financeiro@lexxusadm.com.br', password_hash, 1, 0, 1, 0.0, 0.0, 0.35))
            print("✅ Usuário financeiro@lexxusadm.com.br criado")
        
        # Salvar alterações
        conn.commit()
        
        # Verificar se foi criado/atualizado
        cursor.execute("SELECT id, full_name, email, is_admin FROM users WHERE email = ?", ('financeiro@lexxusadm.com.br',))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Usuário confirmado: ID={user[0]}, Nome={user[1]}, Email={user[2]}, Admin={bool(user[3])}")
        
        conn.close()
        
        print("\n🎉 Conta demo configurada com sucesso!")
        print("\n📧 Credenciais:")
        print("   Email: financeiro@lexxusadm.com.br")
        print("   Senha: FinanceiroDemo2025@")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Adicionando conta demo...")
    success = add_demo_user()
    
    if success:
        print("\n✅ Processo concluído!")
    else:
        print("\n❌ Processo falhou!")