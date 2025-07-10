// Configuração centralizada da API
const API_CONFIG = {
  // Usar variável de ambiente se disponível, senão usar URL padrão
  baseURL: process.env.REACT_APP_API_URL || 'https://bigwhale-backend.onrender.com',
  
  // Configurações gerais otimizadas
  timeout: 15000, // Reduzido para 15 segundos
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  
  // Configurações específicas para diferentes tipos de requisição
  timeouts: {
    auth: 10000,      // Verificação de autenticação: 10 segundos
    login: 20000,     // Login: 20 segundos
    dashboard: 15000, // Dashboard: 15 segundos
    webhook: 5000,    // Webhook: 5 segundos (rápido)
    health: 3000      // Health check: 3 segundos
  }
};

// Função para obter timeout baseado no tipo de requisição
API_CONFIG.getTimeout = (type = 'default') => {
  return API_CONFIG.timeouts[type] || API_CONFIG.timeout;
};

// Log da configuração apenas em desenvolvimento
if (process.env.NODE_ENV === 'development') {
  console.log('🔧 API Config:', {
    baseURL: API_CONFIG.baseURL,
    timeout: API_CONFIG.timeout,
    environment: process.env.REACT_APP_ENVIRONMENT || 'development'
  });
}

export default API_CONFIG;