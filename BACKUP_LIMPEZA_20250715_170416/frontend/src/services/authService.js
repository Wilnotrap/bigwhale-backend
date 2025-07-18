// frontend/src/services/authService.js
import axios from 'axios';
import API_CONFIG from '../config/api';

const API_BASE_URL = API_CONFIG.baseURL;

// Configurar axios para incluir cookies nas requisições
axios.defaults.withCredentials = true;
axios.defaults.headers.post['Content-Type'] = 'application/json';
axios.defaults.headers.put['Content-Type'] = 'application/json';
axios.defaults.headers.patch['Content-Type'] = 'application/json';

// Variável para armazenar callback de logout do contexto
let logoutCallback = null;

// Função para registrar callback de logout
export const setLogoutCallback = (callback) => {
  logoutCallback = callback;
};

// Interceptador para tratar erros 401 (sessão expirada)
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.log('🚨 INTERCEPTADOR 401 ATIVADO!');
      console.log('📍 Caminho atual:', window.location.pathname);
      // Removido console.log com dados sensíveis por segurança
      
      // Sessão expirada - limpar estado
      localStorage.removeItem('user');
      
      // Chamar logout do contexto se disponível
      if (logoutCallback) {
        logoutCallback();
      }
      
      // TEMPORARIAMENTE DESABILITADO - NÃO REDIRECIONAR NO REGISTRO
      if (window.location.pathname === '/register') {
        console.log('🛑 BLOQUEANDO redirecionamento no registro');
        // NÃO redirecionar quando estamos no registro
      } else if (window.location.pathname !== '/login' && window.location.pathname !== '/') {
        console.log('🔀 REDIRECIONANDO para login...');
        // Usar setTimeout para evitar problemas de estado
        setTimeout(() => {
          window.location.href = '/login';
        }, 100);
      }
    }
    return Promise.reject(error);
  }
);

class AuthService {
  async register(userData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, userData);
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async login(credentials) {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, credentials);
      
      // Salvar informações do usuário no localStorage, incluindo as credenciais da API
      if (response.data && response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async logout() {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/logout`);
      return response;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async checkSession() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/session`);
      return response;
    } catch (error) {
      // Melhor tratamento de erro para verificação de sessão
      if (error.response?.status === 401) {
        const sessionError = new Error('Sessão expirada');
        sessionError.status = 401;
        throw sessionError;
      } else if (error.response?.status === 403) {
        const accessError = new Error('Acesso negado');
        accessError.status = 403;
        throw accessError;
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        const networkError = new Error('Erro de rede - verifique sua conexão');
        networkError.status = 0;
        throw networkError;
      }
      throw error.response?.data || new Error('Erro na verificação de sessão');
    }
  }

  async getProfile() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/profile`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async updateProfile(userData) {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/auth/profile`, userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  // Validação de senha no frontend
  validatePassword(password) {
    // eslint-disable-next-line no-useless-escape
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-])[A-Za-z\d@$!%*?&_\-]{8,}$/;
    return passwordRegex.test(password);
  }

  // Validação de email no frontend
  validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  // Obter mensagem de erro de validação de senha
  getPasswordValidationMessage() {
    return 'A senha deve ter pelo menos 8 caracteres, incluindo: maiúscula, minúscula, número e caractere especial (@$!%*?&_-)';
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
const authService = new AuthService();
export default authService;