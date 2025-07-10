// frontend/src/App.js
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Componentes
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import PaymentSuccess from './components/PaymentSuccess';
import Dashboard from './components/Dashboard/Dashboard';
import AdminDashboard from './components/Admin/AdminDashboard';
import NewAdminDashboard from './components/Admin/NewAdminDashboard';
import UserDashboardView from './components/Admin/UserDashboardView';
import UserTrades from './components/Admin/UserTrades';
import UserStats from './components/Admin/UserStats';

// Contextos
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Segurança
import getSecurityMiddleware from './utils/securityMiddleware';
import logger from './utils/logger';

// Configuração da API
import API_CONFIG from './config/api';

// Tema escuro similar ao Binance
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#f0b90b', // Amarelo Binance
    },
    secondary: {
      main: '#1e2329', // Cinza escuro
    },
    background: {
      default: '#0b0e11',
      paper: '#1e2329',
    },
    text: {
      primary: '#ffffff',
      secondary: '#848e9c',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 4,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

// Sistema de keep-alive para manter o Render acordado
const setupKeepAlive = () => {
  const keepAlive = () => {
    fetch(`${API_CONFIG.baseURL}/api/health`, {
      method: 'GET',
      cache: 'no-store'
    })
    .then(response => {
      if (response.ok) {
        console.log('🚀 Keep-alive: Backend acordado');
      }
    })
    .catch(error => {
      console.log('⚠️ Keep-alive: Backend dormindo ou indisponível');
    });
  };

  // Primeira verificação após 30 segundos
  setTimeout(keepAlive, 30000);
  
  // Depois a cada 12 minutos (plano gratuito do Render dorme após 15 minutos)
  setInterval(keepAlive, 12 * 60 * 1000);
};

const AppContent = () => {
  const { user, loading } = useAuth();

  // Função para detectar se o usuário é admin
  const isAdmin = (user) => {
    return user?.email === 'willian@lexxusadm.com.br';
  };

  if (loading) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
        sx={{
          background: 'linear-gradient(135deg, rgba(11, 14, 17, 0.6) 0%, rgba(30, 35, 41, 0.6) 100%)',
        }}
      >
        <Box
          sx={{
            width: 60,
            height: 60,
            border: '4px solid #333',
            borderTop: '4px solid #f0b90b',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            mb: 2,
            '@keyframes spin': {
              '0%': { transform: 'rotate(0deg)' },
              '100%': { transform: 'rotate(360deg)' }
            }
          }}
        />
        <Box
          sx={{
            color: '#f0b90b',
            fontSize: '18px',
            fontWeight: 500,
            textAlign: 'center'
          }}
        >
          Carregando Dashboard...
        </Box>
        <Box
          sx={{
            color: '#848e9c',
            fontSize: '14px',
            mt: 1,
            textAlign: 'center'
          }}
        >
          Verificando autenticação
        </Box>
      </Box>
    );
  }

  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <Box 
          component="main" 
          sx={{ 
            flexGrow: 1, 
            bgcolor: 'background.default'
          }}
        >
          <Routes>
            <Route 
              path="/login" 
              element={
                user ? (isAdmin(user) ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />) : <Login />
              } 
            />
            <Route 
              path="/register" 
              element={
                user ? (isAdmin(user) ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />) : <Register />
              } 
            />
            <Route 
              path="/payment-success" 
              element={<PaymentSuccess />} 
            />
            <Route 
              path="/admin" 
              element={
                user && isAdmin(user) ? <AdminDashboard user={user} /> : <Navigate to="/login" />
              } 
            />
            <Route 
              path="/admin/dashboard" 
              element={
                user && isAdmin(user) ? <NewAdminDashboard /> : <Navigate to="/login" />
              } 
            />
            <Route 
              path="/admin/user/:userId/dashboard" 
              element={
                user && isAdmin(user) ? <UserDashboardView /> : <Navigate to="/login" />
              } 
            />
            <Route 
              path="/admin/user/:userId/trades" 
              element={
                user && isAdmin(user) ? <UserTrades /> : <Navigate to="/login" />
              } 
            />
            <Route 
              path="/admin/user/:userId/stats" 
              element={
                user && isAdmin(user) ? <UserStats /> : <Navigate to="/login" />
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                user ? <Dashboard user={user} /> : <Navigate to="/login" />
              } 
            />
            <Route 
              path="/" 
              element={
                user ? (isAdmin(user) ? <Navigate to="/admin" /> : <Navigate to="/dashboard" />) : <Navigate to="/login" />
              } 
            />
          </Routes>
        </Box>
      </Box>
      
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </Router>
  );
};

function App() {
  useEffect(() => {
    // Configurar segurança
    const securityMiddleware = getSecurityMiddleware();
    
    // Configurar keep-alive para manter o Render acordado
    setupKeepAlive();
    
    // Log de inicialização
    logger.info('Aplicação inicializada');
    
    return () => {
      // Cleanup se necessário
    };
  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;