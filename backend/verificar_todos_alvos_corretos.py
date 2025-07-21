#!/usr/bin/env python3
"""
Script para verificar e corrigir todos os alvos com base nos preços atuais corretos
"""

import sqlite3
import os
import json
import requests

def get_current_price_from_api(symbol):
    """Obtém preço atual da API Bitget"""
    try:
        # Usar endpoint público da Bitget
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

def verificar_todos_alvos_corretos():
    """Verifica e corrige todos os alvos"""
    
    try:
        print("🔧 VERIFICANDO TODOS OS ALVOS CORRETOS")
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
            current_price = get_current_price_from_api(symbol)
            
            if current_price is None:
                print(f"⚠️ Não foi possível obter preço para {symbol}")
                continue
            
            # Calcular alvos atingidos corretamente
            targets_hit_correct = 0
            for target_price in targets:
                if side.lower() == 'long':
                    # Para LONG: alvo é atingido quando preço atual >= preço alvo
                    if current_price >= target_price:
                        targets_hit_correct += 1
                else:
                    # Para SHORT: alvo é atingido quando preço atual <= preço alvo
                    if current_price <= target_price:
                        targets_hit_correct += 1
            
            # Verificar se precisa corrigir
            if targets_hit_correct != targets_hit:
                print(f"🔧 {symbol}: {targets_hit} → {targets_hit_correct} alvos (preço: {current_price})")
                
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
        print(f"   ✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_todos_alvos_corretos() 