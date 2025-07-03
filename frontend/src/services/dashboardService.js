// frontend/src/services/dashboardService.js
import axios from 'axios';
import API_CONFIG from '../config/api';

const API_BASE_URL = API_CONFIG.baseURL;

// Configurar axios para incluir cookies nas requisições
axios.defaults.withCredentials = true;

class DashboardService {
  async getUserStats(startDate = null, endDate = null) {
    try {
      // Construir parâmetros de query se as datas forem fornecidas
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const queryString = params.toString();
      const url = `${API_BASE_URL}/api/dashboard/stats${queryString ? `?${queryString}` : ''}`;
      
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getOpenTrades() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/trades/open`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getClosedTrades() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/trades/closed`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }



  async getProfitCurve() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/profit-curve`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getProfitCurveData() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/profit-curve`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async syncTrades() {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/dashboard/sync-trades`);
      
      // Validar a resposta
      if (!response.data) {
        throw new Error('Resposta inválida do servidor');
      }

      // Verificar se há mensagem de erro específica
      if (response.data.error) {
        throw new Error(response.data.error);
      }

      return response.data;
    } catch (error) {
      console.error('Erro ao sincronizar trades:', error);
      if (error.response?.status === 401) {
        throw new Error('Sessão expirada. Por favor, faça login novamente.');
      } else if (error.response?.status === 400) {
        throw new Error('Credenciais da API não configuradas ou inválidas.');
      }
      throw error.response?.data || { message: 'Erro ao sincronizar trades' };
    }
  }

  async startAutoSync() {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/dashboard/auto-sync/start`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async stopAutoSync() {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/dashboard/auto-sync/stop`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getAutoSyncStatus() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/auto-sync/status`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getAccountBalance() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/account-balance`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getOpenPositions() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/open-positions`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async closePosition(symbol, side) {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/dashboard/close-position`, {
        symbol,
        side
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  // Utilitários para formatação
  formatCurrency(value, currency = 'USDT') {
    if (value === null || value === undefined) return `0 ${currency}`;
    const numValue = parseFloat(value);
    
    // Para valores muito pequenos, mostrar até 8 casas decimais
    if (Math.abs(numValue) < 0.001 && numValue !== 0) {
      return `${numValue.toFixed(8)} ${currency}`;
    }
    
    // Para valores pequenos, mostrar até 6 casas decimais
    if (Math.abs(numValue) < 0.1 && numValue !== 0) {
      return `${numValue.toFixed(6)} ${currency}`;
    }
    
    // Para valores menores que 1, mostrar até 4 casas decimais
    if (Math.abs(numValue) < 1) {
      return `${numValue.toFixed(4)} ${currency}`;
    }
    
    // Para valores maiores, mostrar 2 casas decimais
    return `${numValue.toFixed(2)} ${currency}`;
  }

  formatPercentage(value) {
    if (value === null || value === undefined) return '0%';
    
    // Para percentuais muito pequenos, mostrar mais casas decimais
    if (Math.abs(value) < 0.01 && value !== 0) {
      return `${value >= 0 ? '+' : ''}${parseFloat(value).toFixed(6)}%`;
    }
    
    // Para percentuais pequenos, mostrar 4 casas decimais
    if (Math.abs(value) < 1) {
      return `${value >= 0 ? '+' : ''}${parseFloat(value).toFixed(4)}%`;
    }
    
    // Para percentuais maiores, mostrar 2 casas decimais
    return `${value >= 0 ? '+' : ''}${parseFloat(value).toFixed(2)}%`;
  }

  formatNumber(value, decimals = null) {
    if (decimals === null) {
      // Determinar automaticamente as casas decimais baseado no valor
      if (Math.abs(value) < 0.001 && value !== 0) return parseFloat(value).toFixed(8);
      if (Math.abs(value) < 0.1 && value !== 0) return parseFloat(value).toFixed(6);
      if (Math.abs(value) < 1) return parseFloat(value).toFixed(4);
      return parseFloat(value).toFixed(2);
    }
    return parseFloat(value).toFixed(decimals);
  }

  getColorByValue(value) {
    if (value > 0) return '#02c076'; // Verde
    if (value < 0) return '#f84960'; // Vermelho
    return '#848e9c'; // Cinza neutro
  }

  // Formatação de data
  formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  formatDateShort(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit'
    });
  }

  // Cálculos de trading
  calculateWinRate(trades) {
    if (!trades || trades.length === 0) return 0;
    const winningTrades = trades.filter(trade => (trade.pnl || 0) > 0);
    return (winningTrades.length / trades.length) * 100;
  }

  calculateTotalPnL(trades) {
    if (!trades || trades.length === 0) return 0;
    return trades.reduce((total, trade) => total + (trade.pnl || 0), 0);
  }

  calculateAverageROE(trades) {
    if (!trades || trades.length === 0) return 0;
    const totalROE = trades.reduce((total, trade) => total + (trade.roe || 0), 0);
    return totalROE / trades.length;
  }

  // WebSocket para dados em tempo real (placeholder)
  connectWebSocket(onMessage) {
    // Implementação futura do WebSocket
    console.log('WebSocket connection placeholder');
  }

  disconnectWebSocket() {
    // Implementação futura do WebSocket
    console.log('WebSocket disconnection placeholder');
  }

  async getApiStatus() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/api-status`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getAllPositions() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dashboard/all-positions`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Erro de conexão' };
    }
  }

  async getFinishedPositions(startDate = null, endDate = null) {
    try {
      console.log('Buscando posições finalizadas com filtros:', { startDate, endDate }); // Debug
      
      // Construir parâmetros de query se as datas forem fornecidas (mesmo padrão de getUserStats)
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const queryString = params.toString();
      const url = `${API_BASE_URL}/api/dashboard/finished-positions${queryString ? `?${queryString}` : ''}`;
      
      console.log('URL da requisição:', url); // Debug
      const response = await axios.get(url);
      console.log('Resposta do backend:', response.data); // Debug
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar posições finalizadas:', error);
      throw error.response?.data || { message: 'Erro ao buscar posições finalizadas' };
    }
  }


}

// Objeto que contém todos os métodos do serviço
const dashboardService = new DashboardService();

export default dashboardService;