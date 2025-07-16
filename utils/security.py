# backend/utils/security.py
from flask import current_app
from cryptography.fernet import Fernet, InvalidToken
import base64
import logging

def get_key():
    """
    Obtém a AES_ENCRYPTION_KEY da configuração do Flask e a formata para o Fernet.
    Isso centraliza a gestão de chaves e permite o uso de valores padrão de desenvolvimento.
    """
    # Busca a chave da configuração do aplicativo Flask
    key_str = current_app.config.get('AES_ENCRYPTION_KEY')
    
    if not key_str:
        logging.error("AES_ENCRYPTION_KEY não está configurada no app Flask.")
        raise ValueError("Chave de criptografia não configurada.")
        
    # A chave para o Fernet DEVE ter 32 bytes.
    # Usamos o `ljust` para garantir que a chave tenha o tamanho correto,
    # preenchendo com espaços se for menor e cortando se for maior.
    # O base64 garante que a chave final seja segura para URL.
    key_bytes = key_str.encode('utf-8')
    padded_key = key_bytes.ljust(32)[:32]
    
    return base64.urlsafe_b64encode(padded_key)

def encrypt_api_key(api_key: str) -> str:
    """Criptografa um valor usando a chave de configuração do app (Fernet)."""
    if not api_key:
        return None
    try:
        f = Fernet(get_key())
        encrypted_value = f.encrypt(api_key.encode('utf-8'))
        return encrypted_value.decode('utf-8')
    except Exception as e:
        current_app.logger.error(f"Erro ao criptografar: {e}")
        return None

def get_fallback_keys():
    """Retorna lista de chaves possíveis para fallback em caso de falha na descriptografia"""
    return [
        '12345678901234567890123456789012',  # .env development
        'd9e27b90c839f909cbe3a2e9f3aad8381869bdd04388ea3e7a0735c1659fedde',  # .env.production
        'chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789',  # app.py default
        'a-safe-dev-key-must-be-32-bytes'  # start_server_simple.py default
    ]

def try_decrypt_with_fallback_keys(encrypted_key: str) -> tuple:
    """Tenta descriptografar usando chaves de fallback"""
    fallback_keys = get_fallback_keys()
    
    for key_str in fallback_keys:
        try:
            # Criar chave Fernet a partir da string
            key_bytes = key_str.encode('utf-8')
            padded_key = key_bytes.ljust(32)[:32]
            fernet_key = base64.urlsafe_b64encode(padded_key)
            
            f = Fernet(fernet_key)
            decrypted_value = f.decrypt(encrypted_key.encode('utf-8'))
            return decrypted_value.decode('utf-8'), key_str
        except Exception:
            continue
    
    return None, None

def decrypt_api_key(encrypted_key: str) -> str:
    """Descriptografa um valor usando a chave de configuração do app (Fernet)."""
    if not encrypted_key:
        return None
    
    try:
        # Tentar com a chave atual primeiro
        f = Fernet(get_key())
        decrypted_value = f.decrypt(encrypted_key.encode('utf-8'))
        return decrypted_value.decode('utf-8')
    except InvalidToken:
        # Se falhar, tentar com chaves de fallback
        logging.warning("Chave atual falhou, tentando chaves de fallback...")
        
        decrypted, working_key = try_decrypt_with_fallback_keys(encrypted_key)
        
        if decrypted:
            logging.info(f"Descriptografia bem-sucedida com chave de fallback: {working_key[:20]}...")
            
            # Tentar re-criptografar com a chave atual para corrigir automaticamente
            try:
                from database import db
                current_f = Fernet(get_key())
                new_encrypted = current_f.encrypt(decrypted.encode('utf-8')).decode('utf-8')
                
                # Aqui você poderia implementar lógica para atualizar o banco automaticamente
                # Por enquanto, apenas logamos o sucesso da descriptografia
                logging.info("Dados descriptografados com sucesso usando chave de fallback")
                
            except Exception as e:
                logging.warning(f"Não foi possível re-criptografar automaticamente: {e}")
            
            return decrypted
        else:
            logging.error("Falha na descriptografia: Token inválido com todas as chaves (MAC check failed).")
            return "Decryption failed: MAC check failed"
    except Exception as e:
        logging.error(f"Erro inesperado na descriptografia: {e}")
        return None

# Example usage (for testing purposes, remove from production code if not needed elsewhere)
# if __name__ == '__main__':
#     original_key = "mySuperSecretApiKey123!@#"
#     print(f"Original: {original_key}")
#     encrypted = encrypt_api_key(original_key)
#     print(f"Encrypted: {encrypted}")
#     decrypted = decrypt_api_key(encrypted)
#     print(f"Decrypted: {decrypted}")

#     original_secret = "mySuperSecretApiSecret456$%^"
#     print(f"Original Secret: {original_secret}")
#     encrypted_s = encrypt_api_key(original_secret)
#     print(f"Encrypted Secret: {encrypted_s}")
#     decrypted_s = decrypt_api_key(encrypted_s)
#     print(f"Decrypted Secret: {decrypted_s}")

#     # Test with invalid key
#     print(f"Decrypted (invalid): {decrypt_api_key('invalidb64string')}")
#     print(f"Decrypted (None): {decrypt_api_key(None)}")