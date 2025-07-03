// frontend/src/components/Dashboard/Dashboard.js
import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Menu,
  MenuItem,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  useTheme,
  useMediaQuery,
  Tooltip
} from '@mui/material';
import {
  AccountCircle,
  Logout,
  Refresh,
  Sync,
  Visibility,
  VisibilityOff,
  AdminPanelSettings,
  History,
  Close
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-toastify';
import dashboardService from '../../services/dashboardService';
import logger from '../../utils/logger';
import API_CONFIG from '../../config/api';

import ConsolidatedStatsCard from './ConsolidatedStatsCard';
import OpenPositions from './OpenPositions';
import FinishedOperationsModal from './FinishedOperationsModal';

import Profile from './Profile';
import FuturesBalance from './FuturesBalance';

const Dashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { user, logout, setUser, loading: authLoading } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const [anchorEl, setAnchorEl] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [showFinishedOperations, setShowFinishedOperations] = useState(false);
  const [showSubscription, setShowSubscription] = useState(false);
  const [showCommissionDetails, setShowCommissionDetails] = useState(false);
  const [commissionBalance, setCommissionBalance] = useState(0);
  const [hideValues, setHideValues] = useState(false);
  const [autoSync, setAutoSync] = useState(false);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    setShowProfile(true);
    handleClose();
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      toast.error('Erro ao fazer logout');
    }
    handleClose();
  };

  const handleSync = async () => {
    try {
      await dashboardService.syncTrades();
      toast.success('Trades sincronizados com sucesso');
    } catch (error) {
      toast.error(error.message || 'Erro ao sincronizar trades');
    }
  };

  const toggleAutoSync = async () => {
    try {
      if (autoSync) {
        await dashboardService.stopAutoSync();
        setAutoSync(false);
        toast.info('Auto-sync desativado');
      } else {
        await dashboardService.startAutoSync();
        setAutoSync(true);
        toast.success('Auto-sync ativado');
      }
    } catch (error) {
      toast.error(error.message || 'Erro ao alterar auto-sync');
    }
  };

  const handleUserUpdate = (updatedUser) => {
    setUser(updatedUser);
  };

  const handlePaymentClick = (link) => {
    window.open(link, '_blank', 'noopener,noreferrer');
  };

  const fetchCommissionBalance = async () => {
    try {
      const response = await fetch(`${API_CONFIG.baseURL}/api/dashboard/stats`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data) {
          const totalUsd = result.data.operational_balance_usd || 0;
          const usagePercentage = result.data.operational_balance_percentage || 0;
          const availableUsd = totalUsd - (totalUsd * usagePercentage) / 100;
          setCommissionBalance(availableUsd);
        }
      }
    } catch (error) {
      console.error('Erro ao buscar saldo de comissão:', error);
    }
  };

  useEffect(() => {
    fetchCommissionBalance();
  }, []);

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Barra Superior */}
      <AppBar position="static" color="transparent" elevation={0}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          {/* Nautilus Automação à esquerda com botão admin */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="subtitle1" component="div" sx={{ fontSize: '1.25rem', fontWeight: 600 }}>
              Nautilus Automação
            </Typography>
            {user?.is_admin && (
              <Tooltip title="Painel Admin">
                <IconButton 
                  color="inherit" 
                  onClick={() => navigate('/admin')}
                  sx={{ p: 1 }}
                >
                  <AdminPanelSettings />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          
          {/* Conteúdo central - Bem-vindo, nome do usuário e saldo comissão */}
          <Box sx={{ textAlign: 'center', position: 'absolute', left: '50%', transform: 'translateX(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
            {user?.full_name && (
              <Typography variant="body2" sx={{ 
                color: '#C0C0C0', 
                fontSize: '0.875rem', 
                fontWeight: 'bold' 
              }}>
                Bem-vindo, <span style={{ textDecoration: 'underline' }}>{user.full_name}</span>
              </Typography>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                variant="contained"
                onClick={() => setShowSubscription(true)}
                sx={{
                  backgroundColor: '#87CEEB',
                  color: '#000',
                  fontWeight: 'bold',
                  fontSize: '0.75rem',
                  textTransform: 'none',
                  px: 2,
                  py: 0.5,
                  borderRadius: 2,
                  '&:hover': {
                    backgroundColor: '#6BB6D6'
                  }
                }}
              >
                Assinatura / Renovação
              </Button>
              <Box 
                onClick={() => setShowCommissionDetails(true)}
                sx={{
                  cursor: 'pointer',
                  backgroundColor: 'rgba(102, 126, 234, 0.8)',
                  color: 'white',
                  px: 2,
                  py: 0.5,
                  borderRadius: 2,
                  fontSize: '0.75rem',
                  fontWeight: 'bold',
                  '&:hover': {
                    backgroundColor: 'rgba(102, 126, 234, 1)'
                  }
                }}
              >
                Saldo Comissão: {hideValues ? '••••••' : `$${commissionBalance.toFixed(2)}`}
              </Box>
            </Box>
          </Box>

          {/* Botões de ação */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1.5, 
            minWidth: '200px', 
            justifyContent: 'flex-end',
            flexWrap: 'wrap'
          }}>
            <Tooltip title="Sincronizar trades manualmente">
              <IconButton 
                onClick={handleSync} 
                color="primary"
                sx={{ 
                  p: 1,
                  border: '1px solid',
                  borderColor: 'primary.main',
                  borderRadius: 1
                }}
              >
                <Sync />
              </IconButton>
            </Tooltip>

            <Tooltip title={autoSync ? 'Desativar Auto-Sync' : 'Ativar Auto-Sync'}>
              <Button
                variant="outlined"
                color={autoSync ? 'success' : 'primary'}
                startIcon={<Refresh />}
                onClick={toggleAutoSync}
                size="small"
                sx={{
                  minWidth: '110px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  px: 1.5,
                  py: 0.5,
                  borderRadius: 1.5
                }}
              >
                Auto-Sync {autoSync ? 'ON' : 'OFF'}
              </Button>
            </Tooltip>

            <Tooltip title="Operações Finalizadas">
              <Button
                variant="outlined"
                color="primary"
                startIcon={<History />}
                onClick={() => setShowFinishedOperations(true)}
                size="small"
                sx={{
                  minWidth: '120px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  px: 1.5,
                  py: 0.5,
                  borderRadius: 1.5
                }}
              >
                Operações
              </Button>
            </Tooltip>

            <Tooltip title={hideValues ? 'Mostrar valores' : 'Ocultar valores'}>
              <IconButton 
                onClick={() => setHideValues(!hideValues)}
                sx={{ p: 1 }}
              >
                {hideValues ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </Tooltip>

            <IconButton
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
          </Box>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            onClick={handleClose}
          >
            <MenuItem disabled>
              <Typography variant="body2" color="textSecondary">
                {user?.email} {user?.id && `(ID: #${user.id})`}
              </Typography>
            </MenuItem>
            <MenuItem onClick={handleProfile}>
              <AccountCircle sx={{ mr: 2 }} />
              Perfil
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 2 }} />
              Sair
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Conteúdo Principal */}
      <Container maxWidth="xl">
        <Box sx={{ flexGrow: 1, py: 3 }}>
          <Grid container spacing={3}>
            {/* Saldo da Conta de Futuros */}
            <Grid item xs={12} md={6} lg={6}>
              <FuturesBalance hideValues={hideValues} />
            </Grid>

            {/* Estatísticas Consolidadas */}
            <Grid item xs={12} md={6} lg={6}>
              <ConsolidatedStatsCard hideValues={hideValues} />
            </Grid>

            {/* Posições Abertas */}
            <Grid item xs={12}>
              <OpenPositions user={user} hideValues={hideValues} />
            </Grid>




          </Grid>
        </Box>
      </Container>

      {/* Modal de Perfil */}
      <Profile
        open={showProfile}
        onClose={() => setShowProfile(false)}
        user={user}
        onUserUpdate={handleUserUpdate}
      />

      {/* Modal de Operações Finalizadas */}
      <FinishedOperationsModal
        open={showFinishedOperations}
        onClose={() => setShowFinishedOperations(false)}
        hideValues={hideValues}
      />

      {/* Modal de Detalhes da Comissão */}
      <Dialog 
        open={showCommissionDetails} 
        onClose={() => setShowCommissionDetails(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'hsla(0, 0.00%, 0.00%, 0.93) !important',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(102, 255, 204, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid rgba(102, 255, 204, 0.1)',
          pb: 2,
          fontWeight: 600,
          color: '#66FFCC',
          fontSize: '1.3rem'
        }}>
          Detalhes da Comissão
          <IconButton onClick={() => setShowCommissionDetails(false)} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ py: 4, px: 5 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body1" sx={{ color: 'white', fontWeight: 500 }}>
                Saldo Disponível:
              </Typography>
              <Typography variant="h6" sx={{ color: '#66FFCC', fontWeight: 600 }}>
                ${hideValues ? '••••••' : commissionBalance.toFixed(2)}
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mt: 2 }}>
              Este valor representa o saldo de comissão disponível em sua conta. 
              Para mais detalhes sobre como utilizar este saldo, entre em contato com o suporte.
            </Typography>
          </Box>
        </DialogContent>
      </Dialog>

      {/* Dialog de Assinatura */}
      <Dialog 
        open={showSubscription} 
        onClose={() => setShowSubscription(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'hsla(0, 0.00%, 0.00%, 0.93) !important',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(102, 255, 204, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid rgba(102, 255, 204, 0.1)',
          pb: 2,
          fontWeight: 600,
          color: '#66FFCC',
          fontSize: '1.3rem'
        }}>
          Planos de Assinatura
          <IconButton onClick={() => setShowSubscription(false)} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ py: 4, px: 5, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2.5 }}>
          <Button
            variant="contained"
            onClick={() => handlePaymentClick('https://checkout.grupobigwhale.com/b/14A00l6Ei05a4o04W7gnK02')}
            className="button-plano"
            sx={{
              width: '100%',
              maxWidth: 400,
              py: 2.5,
              mt: 3,
              mb: 2.5,
              fontSize: '1.3rem',
              fontWeight: 800,
              letterSpacing: 0.5,
              transition: 'all 0.3s',
            }}
          >
            Assinatura Mensal
          </Button>
          <Button
            variant="contained"
            onClick={() => handlePaymentClick('https://checkout.grupobigwhale.com/b/4gM14pfaO6tyg6IfALgnK03')}
            className="button-plano"
            sx={{
              width: '100%',
              maxWidth: 400,
              py: 2.5,
              fontSize: '1.3rem',
              fontWeight: 800,
              letterSpacing: 0.5,
              transition: 'all 0.3s',
            }}
          >
            Assinatura Anual
          </Button>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mt: 2, fontStyle: 'italic' }}>
            (Modo sem cobrança de comissão)
          </Typography>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default Dashboard;