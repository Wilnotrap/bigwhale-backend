// frontend/src/components/Dashboard/AccountBalance.js
import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Skeleton,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  useTheme,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp,
  TrendingDown,
  Lock,
  LockOpen,
  Schedule,
  Warning
} from '@mui/icons-material';

const AccountBalance = ({ balance, loading, hideValues = false }) => {
  const theme = useTheme();
  const [progress, setProgress] = useState(0);
  const [debugInfo, setDebugInfo] = useState('');

  // Timer visual de 30 segundos
  useEffect(() => {
    // Iniciar o progresso imediatamente
    setProgress(0);
    
    // Animação contínua do progresso
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          return 0; // Reinicia o ciclo
        }
        return prev + (100 / 300); // 30 segundos = 300 décimos
      });
    }, 100); // Atualiza a cada 100ms
    
    return () => clearInterval(progressInterval);
  }, []);

  // Debug para entender o que está sendo recebido
  useEffect(() => {
    console.log('AccountBalance - balance recebido:', balance);
    if (balance) {
      const balanceData = balance.data || balance;
      console.log('AccountBalance - balanceData:', balanceData);
      console.log('AccountBalance - api_configured:', balanceData?.api_configured);
      setDebugInfo(`API Config: ${balanceData?.api_configured}, Error: ${balanceData?.error || 'none'}`);
    }
  }, [balance]);

  const formatCurrency = (value, currency = 'USDT') => {
    if (hideValues) return `*** ${currency}`;
    if (value === null || value === undefined) return `0.00 ${currency}`;
    const numValue = parseFloat(value);
    // Para valores muito pequenos (< 0.01), usar mais casas decimais
    if (Math.abs(numValue) < 0.01 && numValue !== 0) {
      return `${numValue.toFixed(6)} ${currency}`;
    }
    // Para valores pequenos (< 1), usar 4 casas decimais
    if (Math.abs(numValue) < 1) {
      return `${numValue.toFixed(4)} ${currency}`;
    }
    // Para valores maiores, usar 2 casas decimais
    return `${numValue.toFixed(2)} ${currency}`;
  };

  const formatPercentage = (value) => {
    // Percentuais permanecem visíveis
    if (value === null || value === undefined) return '0.00%';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${parseFloat(value).toFixed(2)}%`;
  };

  // Exibir loading skeleton se estiver carregando
  if (loading) {
    return (
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          Saldo da Conta
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="rectangular" height={40} />
          <Skeleton variant="rectangular" height={40} />
          <Skeleton variant="rectangular" height={40} />
        </Box>
      </Paper>
    );
  }

  if (!balance) {
    return (
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          Saldo da Conta
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 280,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`,
            p: 2
          }}
        >
          <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1.5 }} />
          <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ fontSize: '1rem' }}>
            Erro ao carregar saldo
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ fontSize: '0.85rem' }}>
            Não foi possível conectar com a API da Bitget para obter o saldo da conta.
          </Typography>
        </Box>
      </Paper>
    );
  }
  
  // Verificar se balance.data existe e tem api_configured
  const balanceData = balance.data || balance;
  
  // Debug mais detalhado
  console.log('AccountBalance - balanceData completo:', balanceData);
  console.log('AccountBalance - api_configured:', balanceData?.api_configured);
  console.log('AccountBalance - success:', balanceData?.success);
  
  // Se a API não está configurada E se o success não é true (permitir que dados sejam exibidos mesmo com erro de autenticação temporal)
  if (!balanceData?.api_configured && !balanceData?.success) {
    return (
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          Saldo da Conta
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 280,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`,
            p: 2
          }}
        >
          <Lock sx={{ fontSize: 40, color: 'text.secondary', mb: 1.5 }} />
          <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ fontSize: '1rem' }}>
            API Bitget não configurada
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ fontSize: '0.85rem', mb: 2 }}>
            Configure suas credenciais da API Bitget nas configurações para visualizar o saldo da conta e sincronizar operações.
          </Typography>
          {balanceData?.error && (
            <Alert severity="warning" sx={{ width: '100%', fontSize: '0.8rem' }}>
              {balanceData.error}
            </Alert>
          )}
        </Box>
      </Paper>
    );
  }

  // Se há erro mas a API está configurada
  if (balanceData?.error) {
    return (
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          Saldo da Conta
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 280,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`,
            p: 2
          }}
        >
          <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1.5 }} />
          <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ fontSize: '1rem' }}>
            Erro na conexão com a Bitget
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ fontSize: '0.85rem', mb: 2 }}>
            {balanceData.error}
          </Typography>
          <Alert severity="error" sx={{ width: '100%', fontSize: '0.8rem' }}>
            Verifique suas credenciais da API e tente novamente.
          </Alert>
        </Box>
      </Paper>
    );
  }

  // Processar dados do saldo - agora estrutura simplificada
  const totalEquity = parseFloat(balanceData.total_balance || 0);
  const availableBalance = parseFloat(balanceData.available_balance || 0);
  const unrealizedPnl = parseFloat(balanceData.unrealized_pnl || 0);
  const marginRatio = parseFloat(balanceData.margin_ratio || 0);
  const frozenBalance = totalEquity - availableBalance; // Calcular saldo bloqueado

  const balanceItems = [
    {
      label: 'Saldo Disponível',
      value: formatCurrency(availableBalance),
      description: 'Valor disponível para novas operações',
      color: 'success.main',
      icon: <LockOpen />
    },
    {
      label: 'Saldo Bloqueado',
      value: formatCurrency(frozenBalance),
      description: 'Valor usado como margem em posições abertas',
      color: 'warning.main',
      icon: <Lock />
    },
    {
      label: 'PnL Não Realizado',
      value: formatCurrency(unrealizedPnl),
      description: 'Lucro/prejuízo das posições abertas',
      color: unrealizedPnl >= 0 ? 'success.main' : 'error.main',
      icon: unrealizedPnl >= 0 ? <TrendingUp /> : <TrendingDown />
    }
  ];

  const getMarginRiskLevel = (ratio) => {
    if (ratio >= 80) return { color: 'error', label: 'Alto Risco' };
    if (ratio >= 60) return { color: 'warning', label: 'Risco Médio' };
    if (ratio >= 40) return { color: 'info', label: 'Risco Baixo' };
    return { color: 'success', label: 'Seguro' };
  };

  const marginRisk = getMarginRiskLevel(marginRatio);

  return (
    <Paper sx={{ p: 2.5, height: 380, transition: 'all 0.3s ease-in-out' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '1.1rem' }}>
          <AccountBalanceIcon color="primary" sx={{ fontSize: 20 }} />
          💰 Saldo da Conta
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Timer Visual */}
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
              variant="determinate"
              value={progress}
              size={24}
              thickness={4}
              sx={{
                color: theme.palette.primary.main,
                '& .MuiCircularProgress-circle': {
                  strokeLinecap: 'round',
                }
              }}
            />
            <Box
              sx={{
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Schedule sx={{ fontSize: 12, color: 'text.secondary' }} />
            </Box>
          </Box>
          
          {/* Status da API */}
          <Chip
            label="✅ API Conectada"
            size="small"
            color="success"
            variant="outlined"
            sx={{ fontSize: '0.7rem', height: 20 }}
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
          {formatCurrency(totalEquity)}
        </Typography>
        {marginRatio > 0 && (
          <Chip
            label={`${formatPercentage(marginRatio)} - ${marginRisk.label}`}
            size="small"
            color={marginRisk.color}
            sx={{ mt: 1, fontSize: '0.7rem' }}
          />
        )}
      </Box>

      {/* Lista de Detalhes */}
      <List dense sx={{ py: 0 }}>
        {balanceItems.map((item, index) => (
          <React.Fragment key={index}>
            <ListItem sx={{ px: 0, py: 0.5 }}>
              <Box sx={{ mr: 1, color: item.color, fontSize: '1rem' }}>
                {item.icon}
              </Box>
              <ListItemText
                primary={
                  <Typography variant="body2" sx={{ fontSize: '0.85rem', fontWeight: 500 }}>
                    {item.label}
                  </Typography>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    {item.description}
                  </Typography>
                }
                sx={{ mr: 1 }}
              />
              <Typography 
                variant="body2" 
                sx={{ 
                  fontSize: '0.85rem',
                  fontWeight: 'bold',
                  color: item.color
                }}
              >
                {item.value}
              </Typography>
            </ListItem>
            {index < balanceItems.length - 1 && <Divider sx={{ my: 0.5 }} />}
          </React.Fragment>
        ))}
      </List>

      {/* Debug Info */}
      {process.env.NODE_ENV === 'development' && debugInfo && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem', mt: 1, display: 'block' }}>
          Debug: {debugInfo}
        </Typography>
      )}
    </Paper>
  );
};

export default AccountBalance;