import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Skeleton,
  Chip,
  useTheme,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  AccountBalanceWallet,
  Info
} from '@mui/icons-material';
import dashboardService from '../../services/dashboardService';
import { useAuth } from '../../contexts/AuthContext';

const FuturesBalance = ({ hideValues = false }) => {
  const theme = useTheme();
  const [balanceData, setBalanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Função para formatar moeda
  const formatCurrency = (value, currency = 'USDT') => {
    if (hideValues) return `*** ${currency}`;
    if (value === null || value === undefined || isNaN(value)) return `0.00 ${currency}`;
    const numValue = parseFloat(value);
    return `${numValue.toFixed(2)} ${currency}`;
  };

  // Carregar dados do saldo
  const loadBalance = async (showLoading = false) => {
    try {
      setError(null);
      if (showLoading) {
        setLoading(true);
      }
      console.log('🔍 FuturesBalance: Carregando saldo...');
      
      const response = await dashboardService.getAccountBalance();
      console.log('📡 FuturesBalance: Resposta recebida:', response);
      
      if (response) {
        setBalanceData(response);
        console.log('✅ FuturesBalance: Dados do saldo carregados:', {
          total: response.total_balance,
          available: response.available_balance,
          pnl: response.unrealized_pnl,
          api_configured: response.api_configured
        });
      } else {
        setError('Dados não recebidos do servidor');
      }
    } catch (err) {
      console.error('❌ FuturesBalance: Erro ao carregar saldo:', err);
      setError(err.message || 'Erro ao carregar saldo');
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  // Carregar dados na inicialização
  useEffect(() => {
    loadBalance(true); // Primeira carga com loading
    
    // Atualizar a cada 30 segundos
    const interval = setInterval(() => {
      loadBalance(false); // Atualizações automáticas sem loading
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Exibir loading
  if (loading) {
    return (
      <Paper sx={{ p: 2.5, height: 320 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          💼 Saldo Conta Futuros
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Skeleton variant="rectangular" height={80} />
          <Skeleton variant="rectangular" height={40} />
          <Skeleton variant="rectangular" height={40} />
          <Skeleton variant="rectangular" height={40} />
        </Box>
      </Paper>
    );
  }

  // Exibir erro
  if (error || !balanceData) {
    return (
      <Paper sx={{ p: 2.5, height: 320 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          💼 Saldo Conta Futuros
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 200,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`,
            p: 2
          }}
        >
          <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1.5 }} />
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Erro ao carregar saldo
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
            {error || 'Não foi possível obter os dados da conta de futuros'}
          </Typography>
          <Chip
            label="Tentar Novamente"
            onClick={() => loadBalance(true)}
            color="primary"
            variant="outlined"
            sx={{ cursor: 'pointer' }}
          />
        </Box>
      </Paper>
    );
  }

  // Se API não está configurada
  if (!balanceData.api_configured) {
    return (
      <Paper sx={{ p: 2.5, height: 320 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          💼 Saldo Conta Futuros
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 200,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`,
            p: 2
          }}
        >
          <Warning sx={{ fontSize: 40, color: 'text.secondary', mb: 1.5 }} />
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            API Bitget não configurada
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            Configure suas credenciais da API Bitget no perfil para visualizar o saldo da conta de futuros.
          </Typography>
        </Box>
      </Paper>
    );
  }

  // Processar dados
  const totalBalance = parseFloat(balanceData.total_balance || 0);
  const availableBalance = parseFloat(balanceData.available_balance || 0);
  const unrealizedPnl = parseFloat(balanceData.unrealized_pnl || 0);
  const marginRatio = parseFloat(balanceData.margin_ratio || 0);
  const usedMargin = totalBalance - availableBalance;

  return (
    <Paper sx={{ p: 2.5, height: 320, transition: 'all 0.3s ease-in-out' }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          💼 Saldo Conta Futuros
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            icon={<CheckCircle sx={{ fontSize: 14 }} />}
            label="API Conectada"
            size="small"
            color="success"
            variant="outlined"
            sx={{ fontSize: '0.7rem', height: 24 }}
          />
        </Box>
      </Box>

      {/* Saldo Principal */}
      <Box
        sx={{
          textAlign: 'center',
          p: 2,
          borderRadius: 2,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}20 0%, ${theme.palette.primary.main}10 100%)`,
          mb: 2
        }}
      >
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
          Patrimônio Total
        </Typography>
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 'bold',
            color: theme.palette.primary.main,
            fontSize: '1.8rem'
          }}
        >
          {formatCurrency(totalBalance)}
        </Typography>
        {marginRatio > 0 && (
          <Chip
            label={`Margem: ${marginRatio.toFixed(2)}%`}
            size="small"
            color={marginRatio > 50 ? 'error' : marginRatio > 30 ? 'warning' : 'success'}
            sx={{ mt: 1, fontSize: '0.7rem' }}
          />
        )}
      </Box>

      {/* Detalhes do Saldo */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {/* Saldo Disponível */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 0.5 }}>
            🟢 Disponível
          </Typography>
          <Typography variant="body2" sx={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'success.main' }}>
            {formatCurrency(availableBalance)}
          </Typography>
        </Box>

        {/* Margem Usada */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 0.5 }}>
            🟡 Margem Usada
          </Typography>
          <Typography variant="body2" sx={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'warning.main' }}>
            {formatCurrency(usedMargin)}
          </Typography>
        </Box>

        {/* PnL Não Realizado */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {unrealizedPnl >= 0 ? <TrendingUp sx={{ fontSize: 16 }} /> : <TrendingDown sx={{ fontSize: 16 }} />}
            PnL Não Realizado
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              fontSize: '0.85rem', 
              fontWeight: 'bold', 
              color: unrealizedPnl >= 0 ? 'success.main' : 'error.main'
            }}
          >
            {formatCurrency(unrealizedPnl)}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default FuturesBalance;