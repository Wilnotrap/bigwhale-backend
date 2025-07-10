import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import API_CONFIG from '../config/api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [initialCheckComplete, setInitialCheckComplete] = useState(false);

  const fetchApiCredentialsStatus = useCallback(async (userId) => {
    try {
      const response = await axios.get(`${API_CONFIG.baseURL}/api/credentials/status`, {
        withCredentials: true,
        timeout: API_CONFIG.getTimeout('auth')
      });
      if (response.data.success) {
        return response.data.status.has_credentials;
      }
    } catch (error) {
      console.error('Erro ao verificar status das credenciais da API:', error);
    }
    return false;
  }, []);

  const checkAuth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_CONFIG.baseURL}/api/auth/session`, { 
        withCredentials: true,
        timeout: API_CONFIG.getTimeout('auth')
      });
      
      if (response.data.authenticated) {
        const userData = response.data.user;
        // Verificar se o usuário tem credenciais de API salvas
        const hasApiCredentials = await fetchApiCredentialsStatus(userData.id);
        setUser({ ...userData, hasApiCredentials });
      } else {
        setUser(null);
      }
    } catch (error) {
      // Se for timeout ou erro de conexão, não bloquear a interface
      if (error.code === 'ECONNABORTED' || error.code === 'NETWORK_ERROR') {
        console.log('⚠️ Backend indisponível (cold start?) - carregando interface...');
      } else {
        console.error('Erro ao verificar autenticação:', error.response?.data || error.message || error);
      }
      setUser(null);
    } finally {
      setLoading(false);
      setInitialCheckComplete(true);
    }
  }, [fetchApiCredentialsStatus]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_CONFIG.baseURL}/api/auth/login`, 
        { email, password }, 
        { 
          withCredentials: true,
          timeout: API_CONFIG.getTimeout('login')
        }
      );
      const userData = response.data.user;
      
      // Verificar se o usuário tem credenciais de API salvas após o login
      const hasApiCredentials = await fetchApiCredentialsStatus(userData.id);
      setUser({ ...userData, hasApiCredentials });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API_CONFIG.baseURL}/api/auth/logout`, {}, { 
        withCredentials: true,
        timeout: API_CONFIG.getTimeout('auth')
      });
      setUser(null);
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put(`${API_CONFIG.baseURL}/api/auth/profile`, 
        profileData, 
        { 
          withCredentials: true,
          timeout: API_CONFIG.getTimeout('auth')
        }
      );
      const updatedUser = response.data.user;
      
      setUser(updatedUser);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    updateProfile,
    checkAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext };
export default AuthContext;