#!/usr/bin/env python3
"""
Script para testar o endpoint com autenticação simulada
"""

import requests
import json
import sqlite3
import os

def test_endpoint_with_auth():
    """Testa o endpoint com autenticação simulada"""
    
    try:
        print("🧪 TESTANDO ENDPOINT COM AUTENTICAÇÃO")
        print("=" * 50)
        
        # Primeiro, vamos verificar se há dados no banco
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado: {db_path}")
            return
        
        print(f"✅ Banco encontrado: {db_path}")
        
        # Conectar ao banco e verificar dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_signals'")
        if not cursor.fetchone():
            print("❌ Tabela active_signals não existe")
            conn.close()
            return
        
        # Contar sinais ativos
        cursor.execute("SELECT COUNT(*) FROM active_signals WHERE status = 'active'")
        count = cursor.fetchone()[0]
        print(f"📊 Sinais ativos no banco: {count}")
        
        # Mostrar alguns sinais
        cursor.execute("SELECT id, symbol, side, entry_price, targets_hit FROM active_signals WHERE status = 'active' LIMIT 5")
        signals = cursor.fetchall()
        
        print(f"\n📋 PRIMEIROS SINAIS NO BANCO:")
        for signal in signals:
            print(f"   ID: {signal[0]}, Símbolo: {signal[1]}, Lado: {signal[2]}, Preço: {signal[3]}, Alvos: {signal[4]}")
        
        conn.close()
        
        # Agora vamos simular uma sessão de usuário
        session = requests.Session()
        
        # Fazer login primeiro
        login_url = "http://localhost:5000/api/auth/login"
        login_data = {
            "email": "admin@bigwhale.com",
            "password": "Raikamaster1@"
        }
        
        print(f"\n🔐 Fazendo login...")
        login_response = session.post(login_url, json=login_data, timeout=30)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # Agora testar o endpoint de sinais ativos
            signals_url = "http://localhost:5000/api/dashboard/nautilus-operacional/active-signals-with-targets"
            
            print(f"\n📡 Testando endpoint de sinais ativos...")
            signals_response = session.get(signals_url, timeout=30)
            
            print(f"📊 Status da resposta: {signals_response.status_code}")
            
            if signals_response.status_code == 200:
                try:
                    data = signals_response.json()
                    print("✅ Resposta recebida com sucesso!")
                    
                    if data.get('success'):
                        signals = data.get('data', [])
                        summary = data.get('summary', {})
                        
                        print(f"\n📊 RESUMO:")
                        print(f"   Total de sinais: {summary.get('total_signals', 0)}")
                        print(f"   Alvos atingidos: {summary.get('total_targets_hit', 0)}")
                        print(f"   Sinais com alvos: {summary.get('signals_with_targets', 0)}")
                        print(f"   Sinais completos: {summary.get('completed_signals', 0)}")
                        
                        print(f"\n🎯 SINAIS ATIVOS:")
                        for i, signal in enumerate(signals, 1):
                            print(f"\n   {i}. {signal.get('symbol', 'N/A')} ({signal.get('side', 'N/A').upper()})")
                            print(f"      Preço entrada: ${signal.get('entry_price', 0):.6f}")
                            print(f"      Preço atual: ${signal.get('current_price', 0):.6f}")
                            print(f"      Alvos atingidos: {signal.get('targets_hit', 0)}/{signal.get('total_targets', 0)}")
                            print(f"      Status: {signal.get('status', 'unknown')}")
                            
                            # Mostrar detalhes dos alvos
                            targets_info = signal.get('targets_info', [])
                            if targets_info:
                                print(f"      Alvos:")
                                for target in targets_info:
                                    status = "✓ ATINGIDO" if target.get('is_hit') else "⏳ PENDENTE"
                                    print(f"         {target.get('target_number')}. ${target.get('target_price', 0):.6f} - {status} ({target.get('distance_percent', 0):.1f}%)")
                    
                    else:
                        print(f"❌ Erro na resposta: {data.get('message', 'Erro desconhecido')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao decodificar JSON: {e}")
                    print(f"Resposta: {signals_response.text}")
            
            elif signals_response.status_code == 401:
                print("❌ Erro de autenticação - usuário não logado")
            
            elif signals_response.status_code == 404:
                print("❌ Endpoint não encontrado")
            
            else:
                print(f"❌ Erro HTTP {signals_response.status_code}: {signals_response.text}")
        
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"Resposta: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - servidor não está rodando")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_endpoint_with_auth() 