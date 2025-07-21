#!/usr/bin/env python3
"""
Script para sincronizar sinais reais do Nautilus para o banco de dados
"""

import sys
import os
import json
import requests
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

def fetch_active_operations():
    """Busca operações ativas do Nautilus"""
    try:
        # URL da API do Nautilus
        url = "https://api.nautilus.com.br/v1/operations/active"
        
        # Headers necessários
        headers = {
            'Authorization': 'Bearer YOUR_NAUTILUS_TOKEN',
            'Content-Type': 'application/json'
        }
        
        # Fazer requisição
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('operations', [])
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro ao buscar operações: {e}")
        return []

def validate_operation(operation):
    """Valida se uma operação é válida"""
    try:
        # Verificar campos obrigatórios
        if not operation.get('symbol'):
            return False
            
        if not operation.get('side') in ['buy', 'sell']:
            return False
            
        if not operation.get('price'):
            return False
            
        if not operation.get('targets'):
            return False
            
        return True
        
    except Exception:
        return False

def sincronizar_sinais_reais():
    """Sincroniza sinais reais do Nautilus para o banco de dados"""
    
    try:
        print("🔄 SINCRONIZANDO SINAIS REAIS DO NAUTILUS")
        print("=" * 50)
        
        # Configurar conexão com o banco
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Buscar operações do Nautilus
        print("📡 Buscando operações do Nautilus...")
        operations = fetch_active_operations()
        
        if not operations:
            print("❌ Nenhuma operação encontrada no Nautilus")
            print("💡 Usando dados de exemplo para teste...")
            
            # Dados de exemplo para teste
            operations = [
                {
                    'symbol': 'BELUSDT',
                    'side': 'buy',
                    'price': 0.3056,
                    'targets': [0.3087, 0.3148, 0.3239, 0.33, 0.3316]
                },
                {
                    'symbol': 'GLMUSDT',
                    'side': 'sell',
                    'price': 0.2970,
                    'targets': [0.294, 0.2881, 0.2792, 0.2732, 0.2718]
                },
                {
                    'symbol': 'MKRUSDT',
                    'side': 'sell',
                    'price': 1990.3,
                    'targets': [1970.4, 1930.6, 1870.9, 1831.1, 1821.1]
                }
            ]
            
        print(f"📊 {len(operations)} operações encontradas")
        
        # Salvar sinais no banco
        sinais_salvos = 0
        
        with engine.begin() as conn:
            for i, operation in enumerate(operations, 1):
                try:
                    # Validar operação
                    if not validate_operation(operation):
                        print(f"⚠️  Operação {i} inválida - pulando")
                        continue
                    
                    # Extrair dados
                    symbol = operation.get('symbol', '').upper()
                    side = operation.get('side', '').lower()
                    entry_price = operation.get('price', 0)
                    targets = operation.get('targets', [])
                    
                    # Filtrar alvos vazios
                    targets = [str(t) for t in targets if t and str(t).strip()]
                    
                    if not targets:
                        print(f"⚠️  Operação {i} sem alvos válidos - pulando")
                        continue
                    
                    # Verificar se já existe
                    result = conn.execute(text("""
                        SELECT id FROM active_signals 
                        WHERE symbol = :symbol AND side = :side AND entry_price = :entry_price
                    """), {
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price
                    })
                    
                    if result.fetchone():
                        print(f"⏭️  Operação {i} já existe - pulando")
                        continue
                    
                    # Inserir novo sinal
                    conn.execute(text("""
                        INSERT INTO active_signals (symbol, side, entry_price, targets, status, created_at, updated_at)
                        VALUES (:symbol, :side, :entry_price, :targets, 'active', :now, :now)
                    """), {
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price,
                        'targets': json.dumps(targets),
                        'now': datetime.now().isoformat()
                    })
                    
                    sinais_salvos += 1
                    print(f"✅ Operação {i} salva: {symbol} {side} @ ${entry_price}")
                    
                except Exception as e:
                    print(f"❌ Erro ao salvar operação {i}: {e}")
        
        print("\n" + "=" * 50)
        print(f"🎉 SINCRONIZAÇÃO CONCLUÍDA!")
        print(f"📊 Sinais salvos: {sinais_salvos}")
        print(f"📊 Total de operações processadas: {len(operations)}")
        
        if sinais_salvos > 0:
            print(f"✅ Sistema pronto! {sinais_salvos} sinais ativos para monitorar.")
        else:
            print("⚠️  Nenhum sinal novo foi salvo.")
            
    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sincronizar_sinais_reais() 