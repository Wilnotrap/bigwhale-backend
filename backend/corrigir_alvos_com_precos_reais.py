#!/usr/bin/env python3
"""
Script para corrigir os alvos usando os preços reais da API Bitget
"""

import sqlite3
import os
import json
import requests

def get_current_price_from_bitget(symbol):
    """Obtém preço atual da API Bitget usando endpoint público"""
    try:
        # Usar endpoint público da Bitget para futuros
        response = requests.get(
            f"https://api.bitget.com/api/v2/mix/market/ticker?symbol={symbol}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '00000' and data.get('data'):
                return float(data['data'].get('lastPr', 0))
        
        return None
    except Exception as e:
        print(f"Erro ao obter preço para {symbol}: {e}")
        return None

def corrigir_alvos_com_precos_reais():
    """Corrige os alvos usando preços reais da API"""
    
    try:
        print("🔧 CORRIGINDO ALVOS COM PREÇOS REAIS")
        print("=" * 50)
        
        # Caminho do banco
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado: {db_path}")
            return
        
        print(f"✅ Banco encontrado: {db_path}")
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar todos os sinais
        cursor.execute("SELECT id, symbol, side, entry_price, targets, targets_hit FROM active_signals")
        signals = cursor.fetchall()
        
        print(f"📊 Total de sinais: {len(signals)}")
        
        total_corrigidos = 0
        
        for signal in signals:
            signal_id, symbol, side, entry_price, targets_json, targets_hit = signal
            
            # Converter targets de JSON para lista
            targets = json.loads(targets_json) if targets_json else []
            
            # Obter preço atual da API
            current_price = get_current_price_from_bitget(symbol)
            
            if current_price is None:
                print(f"⚠️ Não foi possível obter preço para {symbol}")
                continue
            
            # Calcular alvos atingidos corretamente
            targets_hit_correct = 0
            targets_info = []
            
            for i, target_price in enumerate(targets):
                is_hit = False
                if side.lower() == 'long':
                    # Para LONG: alvo é atingido quando preço atual >= preço alvo
                    is_hit = current_price >= target_price
                else:
                    # Para SHORT: alvo é atingido quando preço atual <= preço alvo
                    is_hit = current_price <= target_price
                
                if is_hit:
                    targets_hit_correct += 1
                
                targets_info.append({
                    'target': target_price,
                    'is_hit': is_hit
                })
            
            # Verificar se precisa corrigir
            if targets_hit_correct != targets_hit:
                print(f"🔧 {symbol}: {targets_hit} → {targets_hit_correct} alvos (preço: {current_price})")
                print(f"   Lado: {side}, Entrada: {entry_price}")
                for info in targets_info:
                    status = "✅" if info['is_hit'] else "❌"
                    print(f"   {status} Alvo {info['target']}")
                
                cursor.execute(
                    "UPDATE active_signals SET targets_hit = ? WHERE id = ?",
                    (targets_hit_correct, signal_id)
                )
                total_corrigidos += 1
            else:
                print(f"✅ {symbol}: {targets_hit} alvos (preço: {current_price}) - OK")
        
        # Salvar alterações
        conn.commit()
        conn.close()
        
        print(f"\n📈 RESULTADO:")
        print(f"   Total de sinais verificados: {len(signals)}")
        print(f"   Sinais corrigidos: {total_corrigidos}")
        print(f"   ✅ Correção concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    corrigir_alvos_com_precos_reais() 