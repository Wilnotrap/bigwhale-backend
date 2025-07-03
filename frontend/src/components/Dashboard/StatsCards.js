// frontend/src/components/Dashboard/StatsCards.js
import React, { useState, useEffect, useMemo } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Skeleton,
  useTheme,
  CircularProgress,
  Tooltip,
  IconButton,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  ShowChart,
  Timeline,
  Info
} from '@mui/icons-material';
import dashboardService from '../../services/dashboardService';

const StatCard = ({ title, value, secondaryValue, icon, loading, tooltip }) => (
  <Card sx={{ 
    display: 'flex', 
    flexDirection: 'column', 
    justifyContent: 'space-between',
    height: '100%',
    backgroundColor: '#1C2127',
    color: 'white'
  }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {icon}
          <Typography variant="subtitle1" component="div" sx={{ ml: 1, fontWeight: 'bold' }}>
            {title}
          </Typography>
        </Box>
        <Tooltip title={tooltip}>
          <IconButton size="small">
            <Info sx={{ color: 'rgba(255, 255, 255, 0.7)' }} />
          </IconButton>
        </Tooltip>
      </Box>
      <Box sx={{ textAlign: 'right', mt: 2 }}>
        {loading ? (
          <CircularProgress size={30} sx={{ color: 'white' }} />
        ) : (
          <>
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
              {value}
            </Typography>
            {secondaryValue && (
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {secondaryValue}
              </Typography>
            )}
          </>
        )}
      </Box>
    </CardContent>
  </Card>
);

const StatsCards = ({ hideValues = false }) => {
  const theme = useTheme();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [openPositions, setOpenPositions] = useState([]);

  // Carregar dados do dashboard
   useEffect(() => {
     const loadStats = async (showLoading = true) => {
       try {
          if (showLoading) {
            setLoading(true);
          }
          const [statsResponse, apiStatusResponse, openPositionsResponse] = await Promise.all([
            dashboardService.getUserStats(),
            dashboardService.getApiStatus(),
            dashboardService.getOpenPositions()
          ]);
          
          // A resposta vem em response.data quando success = true
          const statsData = statsResponse.data || statsResponse;
          const apiStatusData = apiStatusResponse;
          const openPositionsData = openPositionsResponse.data || [];
          
          // Combinar dados de stats com status da API
          const combinedStats = {
            ...statsData,
            api_status: {
              valid: apiStatusData.configured || false,
              error_message: apiStatusData.configured ? null : 'API não configurada'
            }
          };
          
          setOpenPositions(openPositionsData);
          
          setStats(combinedStats);
        } catch (error) {
          console.error('Erro ao carregar estatísticas:', error);
          setStats(null);
        } finally {
          if (showLoading) {
            setLoading(false);
          }
        }
     };
 
     loadStats(true); // Primeira carga com loading
     
     // Timer para atualização automática a cada 30 segundos (sincronizado com OpenPositions)
     const interval = setInterval(() => {
       loadStats(false); // Atualizações automáticas sem loading
     }, 30000); // 30 segundos
     
     // Cleanup do timer quando o componente for desmontado
     return () => clearInterval(interval);
   }, []);



  const formatCurrency = (value) => {
    if (hideValues) return '$***';
    if (value === null || value === undefined) return '$0.00';
    const numValue = parseFloat(value);
    
    // Para valores muito pequenos, mostrar até 8 casas decimais
    if (Math.abs(numValue) < 0.001 && numValue !== 0) {
      return `$${numValue.toFixed(8)}`;
    }
    // Para valores pequenos, mostrar até 6 casas decimais
    if (Math.abs(numValue) < 0.1 && numValue !== 0) {
      return `$${numValue.toFixed(6)}`;
    }
    // Para valores menores que 1, mostrar até 4 casas decimais
    if (Math.abs(numValue) < 1) {
      return `$${numValue.toFixed(4)}`;
    }
    // Para valores maiores, mostrar 2 casas decimais
    return `$${numValue.toFixed(2)}`;
  };

  const formatBrl = (value) => {
    if (hideValues) return 'R$ ***';
    if (value === null || value === undefined) return 'R$ 0,00';
    return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return '0%';
    
    // Para percentuais muito pequenos, mostrar mais casas decimais
    if (Math.abs(value) < 0.01 && value !== 0) {
      return `${value >= 0 ? '+' : ''}${value.toFixed(6)}%`;
    }
    // Para percentuais pequenos, mostrar 4 casas decimais
    if (Math.abs(value) < 1) {
      return `${value >= 0 ? '+' : ''}${value.toFixed(4)}%`;
    }
    // Para percentuais maiores, mostrar 2 casas decimais
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatNumber = (value) => {
    if (hideValues) return '***';
    if (value === null || value === undefined) return '0';
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const getColorByValue = (value) => {
    if (value > 0) return theme.palette.success.main;
    if (value < 0) return theme.palette.error.main;
    return theme.palette.text.secondary;
  };

  // Calcular ROE das posições abertas - ROE ponderado pela margem
  const calculateOpenROE = () => {
    if (!openPositions || openPositions.length === 0) return 0;
    
    let totalUnrealizedPnl = 0;
    let totalMargin = 0;
    
    openPositions.forEach(position => {
      const unrealized = parseFloat(position.unrealized_pnl || 0);
      const margin = parseFloat(position.margin_size || position.margin || 0);
      
      if (margin > 0) {
        totalUnrealizedPnl += unrealized;
        totalMargin += margin;
      }
    });
    
    if (totalMargin === 0) return 0;
    
    // ROE total = (PnL total não realizado / margem total) * 100
    return (totalUnrealizedPnl / totalMargin) * 100;
  };

  const openROE = calculateOpenROE();

  const statsConfig = [
    {
      title: 'Lucro Aberto',
      value: openROE,
      format: formatPercentage,
      icon: ShowChart,
      color: getColorByValue(openROE || 0),
      description: hideValues ? '*** em operações abertas' : `${formatCurrency(stats?.unrealized_pnl || 0)} em operações abertas`
    },
    {
      title: 'PnL Realizado',
      value: stats?.realized_pnl,
      format: formatCurrency,
      icon: Timeline,
      color: getColorByValue(stats?.realized_pnl || 0),
      description: 'Lucro/Prejuízo de trades fechados'
    },
    {
      title: 'Taxa de Acerto',
      value: stats?.win_rate,
      format: formatPercentage,
      icon: TrendingUp,
      color: getColorByValue(stats?.win_rate || 0),
      description: 'Percentual de trades lucrativos'
    }
  ];

  if (loading) {
    return (
      <Grid container spacing={3}>
        {Array.from({ length: 3 }).map((_, index) => (
          <Grid item xs={12} sm={6} md={4} lg={4} key={index}>
            <Skeleton variant="rectangular" width="100%" height={150} />
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Grid container spacing={3}>
      {statsConfig.map((item, index) => (
        <Grid item xs={12} sm={6} md={4} lg={4} key={index}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" component="div" sx={{ fontWeight: 'bold' }}>
                  {item.title}
                </Typography>
                <Tooltip title={item.description} placement="top">
                  <IconButton size="small">
                    {React.createElement(item.icon, { sx: { color: item.color } })}
                  </IconButton>
                </Tooltip>
              </Box>
              <Box sx={{ textAlign: 'left', mt: 2 }}>
                <Typography variant="h5" component="div" sx={{ fontWeight: 'bold', color: item.color }}>
                  {item.format ? item.format(item.value) : item.value}
                </Typography>
                {item.secondaryValue != null && (
                  <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                    {item.secondaryFormat ? item.secondaryFormat(item.secondaryValue) : item.secondaryValue}
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default StatsCards;