# backend/utils/currency.py
import requests
import logging

def get_brl_to_usd_rate():
    """Obtém a taxa de conversão BRL para USD"""
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/BRL', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['rates']['USD']
        else:
            logging.warning(f"Erro ao obter taxa de câmbio: {response.status_code}")
            return 0.20  # Taxa padrão aproximada
    except Exception as e:
        logging.error(f"Erro ao buscar taxa de câmbio: {e}")
        return 0.20  # Taxa padrão aproximada

def convert_brl_to_usd(amount_brl):
    """Converte valor de BRL para USD"""
    if not amount_brl:
        return 0.0
    
    rate = get_brl_to_usd_rate()
    return float(amount_brl) * rate

def convert_usd_to_brl(amount_usd):
    """Converte valor de USD para BRL"""
    if not amount_usd:
        return 0.0
    
    rate = get_brl_to_usd_rate()
    return float(amount_usd) / rate if rate > 0 else 0.0