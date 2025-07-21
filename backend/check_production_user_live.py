#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar usuário no ambiente de PRODUÇÃO
Conecta ao banco de dados de produção para verificar tellespio93@gmail.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from datetime import datetime
import requests

def check_production_database():
    """Verifica o usuário no banco de dados de produção"""
    try:
        print("🔍 VERIFICANDO USUÁRIO EM PRODUÇÃO")
        print("=" * 50)
        print("📧 Email: tellespio93@gmail.com")
        print("🎫 Código: Bigwhale81#")
        print()
        
        # Caminhos possíveis do banco de produção
        production_db_paths = [
            # Render.com usa /tmp
            '/tmp/site.db',
            # Hostinger ou outros
            os.path.join(os.path.expanduser('~'), 'site.db'),
            # Local mas em produção
            os.path.join('backend', 'instance', 'site.db'),
            # Backup ou cópia
            'production_site.db',
            'site_production.db',
            # Trading signals
            os.path.join('backend', 'trading_signals.db'),
            'trading_signals.db'
        ]
        
        db_found = False
        
        for db_path in production_db_paths:
            if os.path.exists(db_path):
                print(f"📁 Banco encontrado: {db_path}")
                
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Verificar se é o banco correto (tem tabela users)
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                    if not cursor.fetchone():
                        print(f"⚠️  {db_path} não tem tabela 'users', pulando...")
                        conn.close()
                        continue
                    
                    db_found = True
                    print(f"✅ Usando banco de produção: {db_path}")
                    
                    # Buscar o usuário específico
                    email = 'tellespio93@gmail.com'
                    cursor.execute("""
                        SELECT id, full_name, email, is_active, is_admin, 
                               operational_balance, operational_balance_usd,
                               bitget_api_key_encrypted, bitget_api_secret_encrypted, bitget_passphrase_encrypted,
                               created_at, last_login, nautilus_active, nautilus_user_id, commission_rate
                        FROM users 
                        WHERE email = ?
                    """, (email,))
                    
                    user = cursor.fetchone()
                    
                    if user:
                        print("\n🎉 USUÁRIO ENCONTRADO EM PRODUÇÃO!")
                        print("-" * 40)
                        print(f"   🆔 ID: {user[0]}")
                        print(f"   👤 Nome: {user[1]}")
                        print(f"   📧 Email: {user[2]}")
                        print(f"   🟢 Status: {'ATIVO' if user[3] else 'INATIVO'}")
                        print(f"   👑 Admin: {'SIM' if user[4] else 'NÃO'}")
                        print(f"   💰 Saldo BRL: R$ {user[5] or 0:.2f}")
                        print(f"   💵 Saldo USD: $ {user[6] or 0:.2f}")
                        print(f"   🔑 API Key: {'CONFIGURADA' if user[7] else 'NÃO CONFIGURADA'}")
                        print(f"   🔐 API Secret: {'CONFIGURADA' if user[8] else 'NÃO CONFIGURADA'}")
                        print(f"   🔒 Passphrase: {'CONFIGURADA' if user[9] else 'NÃO CONFIGURADA'}")
                        print(f"   📅 Criado em: {user[10]}")
                        print(f"   🕐 Último login: {user[11] or 'NUNCA'}")
                        print(f"   🤖 Nautilus: {'ATIVO' if user[12] else 'INATIVO'}")
                        print(f"   🆔 Nautilus ID: {user[13] or 'NÃO DEFINIDO'}")
                        print(f"   💼 Comissão: {user[14] or 0.35:.2f}%")
                        
                        user_id = user[0]
                        
                        # Verificar sessões ativas
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")
                        if cursor.fetchone():
                            cursor.execute("""
                                SELECT session_token, created_at, last_activity, is_active, ip_address, user_agent
                                FROM user_sessions 
                                WHERE user_id = ?
                                ORDER BY created_at DESC
                                LIMIT 3
                            """, (user_id,))
                            
                            sessions = cursor.fetchall()
                            if sessions:
                                print(f"\n🔐 SESSÕES RECENTES:")
                                print("-" * 40)
                                for i, session in enumerate(sessions, 1):
                                    status = "🟢 ATIVA" if session[3] else "🔴 INATIVA"
                                    print(f"   {i}. Token: {session[0][:20]}...")
                                    print(f"      Status: {status}")
                                    print(f"      Criada: {session[1]}")
                                    print(f"      Atividade: {session[2]}")
                                    print(f"      IP: {session[4] or 'N/A'}")
                                    print()
                        
                        # Verificar trades
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
                        if cursor.fetchone():
                            cursor.execute("""
                                SELECT COUNT(*) as total, 
                                       SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                                       SUM(pnl) as total_pnl
                                FROM trades 
                                WHERE user_id = ? AND status = 'closed'
                            """, (user_id,))
                            
                            trade_stats = cursor.fetchone()
                            if trade_stats and trade_stats[0] > 0:
                                print(f"\n📊 ESTATÍSTICAS DE TRADING:")
                                print("-" * 40)
                                print(f"   📈 Total de trades: {trade_stats[0]}")
                                print(f"   🎯 Trades ganhos: {trade_stats[1]}")
                                print(f"   📉 Trades perdidos: {trade_stats[0] - trade_stats[1]}")
                                print(f"   💰 PnL total: ${trade_stats[2] or 0:.2f}")
                                if trade_stats[0] > 0:
                                    win_rate = (trade_stats[1] / trade_stats[0]) * 100
                                    print(f"   🎯 Taxa de acerto: {win_rate:.1f}%")
                        
                        # Status de confirmação
                        print(f"\n✅ STATUS DE CONFIRMAÇÃO:")
                        print("-" * 40)
                        
                        if user[3]:  # is_active
                            print("   🟢 USUÁRIO ATIVO - Pode fazer login")
                        else:
                            print("   🔴 USUÁRIO INATIVO - Precisa ser ativado")
                        
                        api_configured = bool(user[7] and user[8] and user[9])
                        if api_configured:
                            print("   🟢 API CONFIGURADA - Pode operar")
                        else:
                            print("   🟡 API NÃO CONFIGURADA - Precisa configurar credenciais")
                        
                        if user[12]:  # nautilus_active
                            print("   🟢 NAUTILUS ATIVO - Recebe sinais")
                        else:
                            print("   🟡 NAUTILUS INATIVO - Não recebe sinais")
                        
                        # Ação recomendada
                        print(f"\n🎯 AÇÃO RECOMENDADA:")
                        print("-" * 40)
                        
                        if not user[3]:
                            print("   1. ✅ ATIVAR USUÁRIO no sistema")
                        
                        if not api_configured:
                            print("   2. 🔑 Usuário deve CONFIGURAR API da Bitget")
                        
                        if not user[12]:
                            print("   3. 🤖 ATIVAR NAUTILUS para receber sinais")
                        
                        if user[3] and api_configured and user[12]:
                            print("   ✅ USUÁRIO TOTALMENTE CONFIGURADO!")
                        
                        conn.close()
                        return True
                    
                    else:
                        print(f"❌ Usuário não encontrado em {db_path}")
                        
                        # Verificar usuários similares
                        cursor.execute("SELECT email FROM users WHERE email LIKE ?", ('%telles%',))
                        similar = cursor.fetchall()
                        if similar:
                            print(f"🔍 Usuários similares em {db_path}:")
                            for email in similar:
                                print(f"   - {email[0]}")
                    
                    conn.close()
                    
                except Exception as e:
                    print(f"❌ Erro ao acessar {db_path}: {e}")
                    continue
        
        if not db_found:
            print("❌ NENHUM BANCO DE PRODUÇÃO ENCONTRADO!")
            print("\n🔍 Caminhos verificados:")
            for path in production_db_paths:
                exists = "✅" if os.path.exists(path) else "❌"
                print(f"   {exists} {path}")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_production_api():
    """Verifica se o usuário existe via API de produção"""
    try:
        print(f"\n🌐 VERIFICANDO VIA API DE PRODUÇÃO:")
        print("-" * 40)
        
        # URLs possíveis de produção
        production_urls = [
            "https://bwhale.site",
            "http://bwhale.site",
            "https://bigwhale-production.onrender.com",
            "http://localhost:5000"  # Se estiver rodando local em produção
        ]
        
        for base_url in production_urls:
            try:
                print(f"🔍 Testando: {base_url}")
                
                # Testar health check
                health_response = requests.get(f"{base_url}/api/health", timeout=10)
                
                if health_response.status_code == 200:
                    print(f"✅ Servidor de produção ativo: {base_url}")
                    
                    # Tentar fazer login para verificar se o usuário existe
                    login_data = {
                        "email": "tellespio93@gmail.com",
                        "password": "senha_teste"  # Senha qualquer para testar se o usuário existe
                    }
                    
                    login_response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
                    
                    if login_response.status_code == 401:
                        response_data = login_response.json()
                        if "senha" in response_data.get('message', '').lower() or "password" in response_data.get('message', '').lower():
                            print("✅ USUÁRIO EXISTE - Senha incorreta (normal)")
                            return True
                        elif "não encontrado" in response_data.get('message', '').lower() or "not found" in response_data.get('message', '').lower():
                            print("❌ Usuário não encontrado na API")
                    elif login_response.status_code == 200:
                        print("⚠️  Login realizado (senha fraca?)")
                        return True
                    else:
                        print(f"⚠️  Resposta inesperada: {login_response.status_code}")
                
                else:
                    print(f"❌ Servidor não respondeu: {health_response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão: {e}")
                continue
        
        return False
        
    except Exception as e:
        print(f"❌ Erro na verificação via API: {e}")
        return False

if __name__ == '__main__':
    print("🚀 VERIFICAÇÃO DE USUÁRIO EM PRODUÇÃO")
    print("Email: tellespio93@gmail.com")
    print("Código de convite: Bigwhale81#")
    print()
    
    # Verificar banco de dados
    db_success = check_production_database()
    
    # Verificar via API se não encontrou no banco
    if not db_success:
        api_success = check_production_api()
        
        if not api_success:
            print(f"\n❌ USUÁRIO NÃO ENCONTRADO EM PRODUÇÃO")
            print("💡 Possíveis causas:")
            print("   - Usuário ainda não se cadastrou")
            print("   - Erro no processo de cadastro")
            print("   - Banco de dados diferente")
            print("   - Servidor de produção em local diferente")
    
    print(f"\n{'='*50}")
    print("🏁 VERIFICAÇÃO CONCLUÍDA")