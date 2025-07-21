#!/usr/bin/env python3
"""
Script para testar a correção da sincronização
"""

import requests
import json
from services.nautilus_service import nautilus_service

def test_sync_fix():
    """Testa a correção da sincronização"""
    
    print("🧪 TESTE DA CORREÇÃO DE SINCRONIZAÇÃO")
    print("=" * 50)
    
    try:
        # Garantir autenticação
        auth_result = nautilus_service.ensure_authenticated()
        if not auth_result['success']:
            print(f"❌ Falha na autenticação: {auth_result.get('error')}")
            return
        
        print("✅ Autenticação OK")
        
        # Buscar operações ativas
        url = f"{nautilus_service.base_url}/operation/active-operations"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'{nautilus_service.token}',
            'auth-userid': str(nautilus_service.user_id)
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            operations_data = response.json()
            
            print(f"📊 Total de operações recebidas: {len(operations_data) if isinstance(operations_data, list) else 0}")
            
            if isinstance(operations_data, list):
                print(f"\n🔍 TESTANDO NOVA LÓGICA:")
                print("-" * 50)
                
                valid_operations = 0
                
                for i, operation in enumerate(operations_data):
                    print(f"\n📋 Operação {i+1}: {operation.get('symbol')} {operation.get('side')}")
                    
                    # Extrair dados essenciais (nova lógica)
                    symbol = operation.get('symbol', '').replace('USDT', '') + 'USDT'
                    side = operation.get('side', '').lower()
                    entry_price = operation.get('price') or operation.get('entry_price') or operation.get('entryPrice')
                    
                    print(f"   Símbolo: {symbol}")
                    print(f"   Lado: {side}")
                    print(f"   Preço entrada: {entry_price}")
                    
                    # Extrair alvos (nova lógica)
                    targets = []
                    
                    # Formato 2: alvos individuais (target1, target2, etc.)
                    if any(f'target{i}' in operation for i in range(1, 6)):
                        for i in range(1, 6):
                            target_key = f'target{i}'
                            if target_key in operation and operation[target_key] is not None and operation[target_key] != '':
                                targets.append(float(operation[target_key]))
                        print(f"   Alvos: {targets}")
                    
                    # Verificar se é válida
                    is_valid = bool(symbol and side and targets and entry_price)
                    
                    if is_valid:
                        print(f"   ✅ VÁLIDA - Será salva")
                        valid_operations += 1
                    else:
                        print(f"   ❌ INVÁLIDA - Será ignorada")
                        print(f"      Motivo: symbol={bool(symbol)}, side={bool(side)}, targets={len(targets)}, entry_price={bool(entry_price)}")
                
                print(f"\n📊 RESUMO:")
                print(f"✅ Operações válidas: {valid_operations}")
                print(f"❌ Operações inválidas: {len(operations_data) - valid_operations}")
                print(f"📊 Total: {len(operations_data)}")
                
                if valid_operations > 0:
                    print(f"\n🎉 CORREÇÃO FUNCIONOU!")
                    print(f"   - Agora temos {valid_operations} operações válidas")
                    print(f"   - Antes: 0 operações válidas")
                    print(f"   - Melhoria: +{valid_operations} operações")
                else:
                    print(f"\n❌ Ainda há problemas")
                
            else:
                print(f"❌ Dados não são uma lista: {type(operations_data)}")
                
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sync_fix() 