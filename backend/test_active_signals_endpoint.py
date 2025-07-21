#!/usr/bin/env python3
"""
Script para testar o endpoint de sinais ativos com alvos
"""

import requests
import json

def test_active_signals_endpoint():
    """Testa o endpoint de sinais ativos com alvos"""
    
    try:
        print("🧪 TESTANDO ENDPOINT DE SINAIS ATIVOS COM ALVOS")
        print("=" * 50)
        
        # URL do endpoint
        url = "http://localhost:5000/api/dashboard/nautilus-operacional/active-signals-with-targets"
        
        # Headers necessários
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
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
                        print(f"\n   {i}. {signal.get('symbol')} ({signal.get('side').upper()})")
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
                print(f"Resposta: {response.text}")
        
        elif response.status_code == 401:
            print("❌ Erro de autenticação - usuário não logado")
        
        elif response.status_code == 404:
            print("❌ Endpoint não encontrado")
        
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - servidor não está rodando")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_active_signals_endpoint() 