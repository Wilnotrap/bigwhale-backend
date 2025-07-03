// Configuração centralizada da API
const API_CONFIG = {
  // Usar variável de ambiente se disponível, senão usar URL padrão
  baseURL: process.env.REACT_APP_API_URL || 'https://bigwhale-backend.onrender.com',
  
  // Configurações gerais
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
};

// Log da configuração apenas em desenvolvimento
if (process.env.NODE_ENV === 'development') {
  console.log('API Config:', {
    baseURL: API_CONFIG.baseURL,
    environment: process.env.REACT_APP_ENVIRONMENT || 'development'
  });
}

export default API_CONFIG;