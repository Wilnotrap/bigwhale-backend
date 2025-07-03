import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import API_CONFIG from '../config/api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Função para criptografar dados sensíveis antes de salvar no localStorage
  const encryptData = (data) => {
    // Usamos btoa para uma codificação básica, já que os dados já vêm criptografados do backend
    return btoa(JSON.stringify(data));
  };

  // Função para descriptografar dados do localStorage
  const decryptData = (encryptedData) => {
    try {
      return JSON.parse(atob(encryptedData));
    } catch {
      return null;
    }
  };

  // Função para salvar credenciais no localStorage
  const saveCredentials = (credentials) => {
    if (!credentials) return;
    const encryptedData = encryptData(credentials);
    localStorage.setItem('bitget_credentials', encryptedData);
  };

  // Função para recuperar credenciais do localStorage
  const getCredentials = () => {
    const encryptedData = localStorage.getItem('bitget_credentials');
    if (!encryptedData) return null;
    return decryptData(encryptedData);
  };

  const checkAuth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_CONFIG.baseURL}/api/auth/session`, { withCredentials: true });
      if (response.data.authenticated) {
        const userData = response.data.user;
        // Recupera as credenciais salvas
        const savedCredentials = getCredentials();
        if (savedCredentials) {
          userData.bitget_api_key = savedCredentials.bitget_api_key;
          userData.bitget_api_secret = savedCredentials.bitget_api_secret;
          userData.bitget_passphrase = savedCredentials.bitget_passphrase;
        }
        setUser(userData);
      } else {
        setUser(null);
        localStorage.removeItem('bitget_credentials');
      }
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error);
      setUser(null);
      localStorage.removeItem('bitget_credentials');
    } finally {
      setLoading(false);
    }
  }, [API_CONFIG.baseURL]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_CONFIG.baseURL}/api/auth/login`, { email, password }, { withCredentials: true });
      const userData = response.data.user;
      
      // Salva as credenciais da API no localStorage
      if (userData.bitget_api_key && userData.bitget_api_secret && userData.bitget_passphrase) {
        saveCredentials({
          bitget_api_key: userData.bitget_api_key,
          bitget_api_secret: userData.bitget_api_secret,
          bitget_passphrase: userData.bitget_passphrase
        });
      }
      
      setUser(userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API_CONFIG.baseURL}/api/auth/logout`, {}, { withCredentials: true });
      setUser(null);
      localStorage.removeItem('bitget_credentials');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put(`${API_CONFIG.baseURL}/api/auth/profile`, profileData, { withCredentials: true });
      const updatedUser = response.data.user;
      
      // Atualiza as credenciais no localStorage se fornecidas
      if (profileData.bitget_api_key && profileData.bitget_api_secret && profileData.bitget_passphrase) {
        saveCredentials({
          bitget_api_key: profileData.bitget_api_key,
          bitget_api_secret: profileData.bitget_api_secret,
          bitget_passphrase: profileData.bitget_passphrase
        });
      }
      
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
      {!loading && children}
    </AuthContext.Provider>
  );
};

export { AuthContext };
export default AuthContext;