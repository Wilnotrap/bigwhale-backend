# backend/utils/api_persistence.py
import json
import os
from datetime import datetime

class APIPersistence:
    """Classe para persistir dados de API temporariamente"""
    
    def __init__(self):
        self.data_file = '/tmp/api_data.json'
    
    def save_data(self, key, data):
        """Salva dados com uma chave específica"""
        try:
            # Carregar dados existentes
            existing_data = self.load_all_data()
            
            # Adicionar novos dados com timestamp
            existing_data[key] = {
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Salvar de volta
            with open(self.data_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False
    
    def load_data(self, key):
        """Carrega dados por chave específica"""
        try:
            all_data = self.load_all_data()
            return all_data.get(key, {}).get('data')
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return None
    
    def load_all_data(self):
        """Carrega todos os dados salvos"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erro ao carregar todos os dados: {e}")
            return {}
    
    def delete_data(self, key):
        """Remove dados por chave específica"""
        try:
            all_data = self.load_all_data()
            if key in all_data:
                del all_data[key]
                with open(self.data_file, 'w') as f:
                    json.dump(all_data, f, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Erro ao deletar dados: {e}")
            return False

api_persistence = APIPersistence()