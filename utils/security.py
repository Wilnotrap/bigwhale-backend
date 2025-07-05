# backend/utils/security.py
from flask import current_app
from cryptography.fernet import Fernet, InvalidToken
import base64
import logging

def get_key():
    """Obtém a AES_ENCRYPTION_KEY da configuração do Flask e a formata para o Fernet"""
    key_str = current_app.config.get('AES_ENCRYPTION_KEY')
    
    if not key_str:
        logging.error("AES_ENCRYPTION_KEY não está configurada no app Flask.")
        raise ValueError("Chave de criptografia não configurada.")
        
    key_bytes = key_str.encode('utf-8')
    padded_key = key_bytes.ljust(32)[:32]
    
    return base64.urlsafe_b64encode(padded_key)

def encrypt_api_key(api_key: str) -> str:
    """Criptografa um valor usando a chave de configuração do app (Fernet)"""
    if not api_key:
        return None
    try:
        f = Fernet(get_key())
        encrypted_value = f.encrypt(api_key.encode('utf-8'))
        return encrypted_value.decode('utf-8')
    except Exception as e:
        current_app.logger.error(f"Erro ao criptografar: {e}")
        return None

def decrypt_api_key(encrypted_key: str) -> str:
    """Descriptografa um valor usando a chave de configuração do app (Fernet)"""
    if not encrypted_key:
        return None
    
    try:
        f = Fernet(get_key())
        decrypted_value = f.decrypt(encrypted_key.encode('utf-8'))
        return decrypted_value.decode('utf-8')
    except InvalidToken:
        logging.error("Falha na descriptografia: Token inválido.")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado na descriptografia: {e}")
        return None