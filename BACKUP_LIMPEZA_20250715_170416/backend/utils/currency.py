import requests
import logging

logger = logging.getLogger(__name__)

def get_brl_to_usd_rate():
    """
    Busca a taxa de conversão atual de BRL para USD.
    Retorna uma taxa de fallback em caso de erro.
    """
    try:
        # Usando uma API pública e confiável para taxas de câmbio
        response = requests.get('https://api.exchangerate-api.com/v4/latest/BRL', timeout=5)
        response.raise_for_status()
        data = response.json()
        rate = data.get('rates', {}).get('USD')
        if rate:
            logger.info(f"Taxa de conversão BRL -> USD obtida com sucesso: {rate}")
            return float(rate)
        else:
            logger.warning("Resposta da API de câmbio não continha a taxa USD. Usando fallback.")
            return 0.20  # Fallback
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar taxa de conversão: {e}. Usando fallback.")
        # Fallback para uma taxa fixa em caso de erro na API
        return 0.20  # Aprox. 1 BRL = 0.20 USD 