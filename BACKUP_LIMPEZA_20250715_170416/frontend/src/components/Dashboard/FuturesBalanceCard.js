// frontend/src/components/Dashboard/FuturesBalanceCard.js
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  IconButton,
  Tooltip,
  Chip
} from '@mui/material';
import {
  AccountBalance,
  Refresh,
  TrendingUp,
  TrendingDown,
  Info
} from '@mui/icons-material';
import dashboardService from '../../services/dashboardService';

const FuturesBalanceCard = ({ hideValues = false }) => {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadBalance = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      setError(null);
      const response = await dashboardService.getAccountBalance();
      
      if (response.success) {
        setBalance(response.data);
      } else {
        setError('Erro ao carregar saldo');
      }
    } catch (error) {
      console.error('Erro ao carregar saldo:', error);
      setError(error.message || 'Erro ao carregar saldo');
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  // Auto-refresh silencioso a cada 30 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      loadBalance(false); // Refresh silencioso sem loading
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadBalance(true); // Primeira carga com loading
  }, []);

  const formatCurrency = (value) => {
    if (hideValues) return '***';
    if (value === null || value === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }).format(value);
  };

  const getUnrealizedPnlColor = (value) => {
    if (!value || value === 0) return '#ffffff';
    return value > 0 ? '#4caf50' : '#f44336';
  };

  const getMarginRatioColor = (ratio) => {
    if (ratio < 50) return '#4caf50'; // Verde - seguro
    if (ratio < 80) return '#ff9800'; // Laranja - atenção
    return '#f44336'; // Vermelho - perigo
  };

  return (
    <Card sx={{ 
      backgroundColor: '#1C2127',
      color: 'white',
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AccountBalance sx={{ color: '#66FFCC', mr: 1 }} />
            <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
              Saldo Futuros
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Tooltip title="Atualizar saldo">
              <span>
                <IconButton 
                  size="small" 
                  onClick={loadBalance}
                  disabled={loading}
                  sx={{ color: 'white', mr: 1 }}
                >
                  <Refresh sx={{ fontSize: 18 }} />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="Saldo da conta de futuros na Bitget">
              <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                <Info sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress size={40} sx={{ color: '#66FFCC' }} />
          </Box>
        ) : error ? (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="body2" color="error">
              {error}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Verifique suas credenciais da API
            </Typography>
          </Box>
        ) : balance ? (
          <Box>
            {/* Layout Horizontal - Linha Principal */}
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
              gap: 3,
              mb: 2
            }}>
              {/* Saldo Total */}
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Patrimônio Total
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#66FFCC' }}>
                  {formatCurrency(balance.total_balance)}
                </Typography>
              </Box>

              {/* Saldo Disponível */}
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Saldo Disponível
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  {formatCurrency(balance.available_balance)}
                </Typography>
              </Box>

              {/* PnL Não Realizado */}
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  PnL Não Realizado
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {balance.unrealized_pnl > 0 ? (
                    <TrendingUp sx={{ color: '#4caf50', mr: 0.5, fontSize: 18 }} />
                  ) : balance.unrealized_pnl < 0 ? (
                    <TrendingDown sx={{ color: '#f44336', mr: 0.5, fontSize: 18 }} />
                  ) : null}
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontWeight: 'bold',
                      color: getUnrealizedPnlColor(balance.unrealized_pnl)
                    }}
                  >
                    {formatCurrency(balance.unrealized_pnl)}
                  </Typography>
                </Box>
              </Box>

              {/* Taxa de Margem */}
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Taxa de Margem
                </Typography>
                <Chip
                  label={`${hideValues ? '***' : (balance.margin_ratio * 100).toFixed(2)}%`}
                  size="medium"
                  sx={{
                    backgroundColor: `${getMarginRatioColor(balance.margin_ratio * 100)}20`,
                    color: getMarginRatioColor(balance.margin_ratio * 100),
                    fontWeight: 'bold',
                    fontSize: '0.9rem'
                  }}
                />
              </Box>
            </Box>

            {/* Status da API - Linha Inferior */}
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center',
              pt: 2, 
              borderTop: '1px solid rgba(255, 255, 255, 0.1)' 
            }}>
              <Chip
                label={balance.api_configured ? 'API Conectada' : 'API Não Configurada'}
                size="small"
                color={balance.api_configured ? 'success' : 'error'}
                variant="outlined"
              />
            </Box>
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Nenhum dado disponível
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default FuturesBalanceCard;