#!/usr/bin/env python3
"""
Script para debugar as operações do Nautilus
"""

import requests
import json
from services.nautilus_service import nautilus_service

def debug_operations():
    """Debuga as operações do Nautilus"""
    
    print("🔍 DEBUG DAS OPERAÇÕES DO NAUTILUS")
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
        
        print(f"🌐 Buscando operações em: {url}")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            operations_data = response.json()
            
            print(f"📊 Total de operações recebidas: {len(operations_data) if isinstance(operations_data, list) else 0}")
            
            if isinstance(operations_data, list):
                print(f"\n🔍 ANALISANDO CADA OPERAÇÃO:")
                print("-" * 50)
                
                valid_operations = 0
                invalid_operations = 0
                
                for i, operation in enumerate(operations_data):
                    print(f"\n📋 Operação {i+1}:")
                    
                    # Extrair dados essenciais
                    symbol = operation.get('symbol', '').replace('USDT', '') + 'USDT'
                    side = operation.get('side', '').lower()
                    entry_price = operation.get('entry_price') or operation.get('entryPrice')
                    
                    print(f"   Símbolo: {symbol}")
                    print(f"   Lado: {side}")
                    print(f"   Preço entrada: {entry_price}")
                    
                    # Extrair alvos
                    targets = []
                    
                    # Formato 1: targets como lista
                    if 'targets' in operation and isinstance(operation['targets'], list):
                        targets = [float(t) for t in operation['targets'] if t is not None]
                        print(f"   Alvos (lista): {targets}")
                    
                    # Formato 2: alvos individuais (target1, target2, etc.)
                    elif any(f'target{i}' in operation for i in range(1, 6)):
                        for i in range(1, 6):
                            target_key = f'target{i}'
                            if target_key in operation and operation[target_key] is not None:
                                targets.append(float(operation[target_key]))
                        print(f"   Alvos (target1-5): {targets}")
                    
                    # Formato 3: tp1, tp2, tp3, etc.
                    elif any(f'tp{i}' in operation for i in range(1, 6)):
                        for i in range(1, 6):
                            tp_key = f'tp{i}'
                            if tp_key in operation and operation[tp_key] is not None:
                                targets.append(float(operation[tp_key]))
                        print(f"   Alvos (tp1-5): {targets}")
                    
                    # Verificar se é válida
                    is_valid = bool(symbol and side and targets and entry_price)
                    
                    if is_valid:
                        print(f"   ✅ VÁLIDA - Será salva")
                        valid_operations += 1
                    else:
                        print(f"   ❌ INVÁLIDA - Será ignorada")
                        print(f"      Motivo: symbol={bool(symbol)}, side={bool(side)}, targets={bool(targets)}, entry_price={bool(entry_price)}")
                        invalid_operations += 1
                    
                    # Mostrar estrutura completa para debug
                    print(f"   📄 Estrutura completa: {json.dumps(operation, indent=2)}")
                
                print(f"\n📊 RESUMO:")
                print(f"✅ Operações válidas: {valid_operations}")
                print(f"❌ Operações inválidas: {invalid_operations}")
                print(f"📊 Total: {len(operations_data)}")
                
                if valid_operations != 3:
                    print(f"\n⚠️  PROBLEMA IDENTIFICADO:")
                    print(f"   - Esperado: 3 sinais salvos")
                    print(f"   - Encontrado: {valid_operations} operações válidas")
                    print(f"   - Diferença: {valid_operations - 3}")
                
            else:
                print(f"❌ Dados não são uma lista: {type(operations_data)}")
                print(f"📄 Conteúdo: {operations_data}")
                
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_operations() 