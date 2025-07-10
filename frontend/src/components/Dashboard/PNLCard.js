// frontend/src/components/Dashboard/PNLCard.js
import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Skeleton
} from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import './PNLCard.css';


const PNLCard = ({ data, loading, hideValues = false, stats = null }) => {
  const formatCurrency = (value) => {
    if (hideValues) return '$***';
    if (value === null || value === undefined) return '$0.00';
    const numValue = parseFloat(value);
    // Para valores muito pequenos (< 0.01), usar mais casas decimais
    if (Math.abs(numValue) < 0.01 && numValue !== 0) {
      return `$${numValue.toFixed(8)}`;
    }
    // Para valores pequenos (< 1), usar 6 casas decimais para mostrar precisão
    if (Math.abs(numValue) < 1) {
      return `$${numValue.toFixed(6)}`;
    }
    // Para valores maiores, usar 4 casas decimais para manter precisão
    return `$${numValue.toFixed(4)}`;
  };

  const formatPercentage = (value) => {
    // Percentuais permanecem visíveis
    if (value === null || value === undefined) return '0.00%';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${parseFloat(value).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <Paper 
        sx={{ 
          p: 3, 
          height: 380,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center'
        }}
      >
        <Skeleton variant="text" width="60%" height={40} />
        <Skeleton variant="text" width="80%" height={60} sx={{ mt: 2 }} />
        <Skeleton variant="text" width="40%" height={30} sx={{ mt: 1 }} />
      </Paper>
    );
  }

  // Priorizar dados das estatísticas se disponíveis, senão usar curva de lucro
  let currentPnL, realizedPnL, unrealizedPnL, pnlChange, pnlChangePercent;
  
  if (stats) {
    // Usar dados das estatísticas (mais precisos)
    currentPnL = stats.total_pnl || 0;
    realizedPnL = stats.realized_pnl || 0;
    unrealizedPnL = stats.unrealized_pnl || 0;
    
    // Calcular variação baseada no P&L não realizado
    pnlChange = unrealizedPnL;
    
    // Para o percentual, usar uma lógica mais apropriada:
    // Se há P&L realizado significativo (> $1), calcular baseado nele
    // Caso contrário, não mostrar percentual ou mostrar baseado em valor fixo
    if (Math.abs(realizedPnL) > 1) {
      // Percentual baseado no retorno total sobre o P&L realizado
      pnlChangePercent = (currentPnL / Math.abs(realizedPnL)) * 100;
    } else if (Math.abs(currentPnL) < 0.1) {
      // Para valores muito pequenos, mostrar 0%
      pnlChangePercent = 0;
    } else {
      // Para casos sem base de cálculo adequada, não mostrar percentual extremo
      pnlChangePercent = currentPnL > 0 ? 1 : -1; // Mostrar +1% ou -1% simbólico
    }
  } else {
    // Fallback para curva de lucro
    currentPnL = data && data.length > 0 ? data[data.length - 1]?.cumulative_pnl || 0 : 0;
    const previousPnL = data && data.length > 1 ? data[data.length - 2]?.cumulative_pnl || 0 : 0;
    realizedPnL = currentPnL;
    unrealizedPnL = 0;
    pnlChange = currentPnL - previousPnL;
    pnlChangePercent = previousPnL !== 0 ? ((pnlChange / Math.abs(previousPnL)) * 100) : 0;
  }
  
  const isPositive = currentPnL >= 0;

  // Removidas todas as funções não utilizadas: SunEffect, RainEffect, LightningEffect, OceanWaves, WeatherEffects

  return (
    <Paper 
      sx={{ 
        p: 3,
        height: 380,
        borderRadius: 2,
        background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        color: 'white',
        position: 'relative'
      }}
    >
      
      <Box 
        sx={{ 
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}
      >
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isPositive ? (
            <TrendingUp sx={{ color: '#4caf50', fontSize: 28 }} />
          ) : (
            <TrendingDown sx={{ color: '#f44336', fontSize: 28 }} />
          )}
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 600
            }}
          >
            P&L Total
          </Typography>
        </Box>

        {/* Main PNL Value */}
        <Box sx={{ textAlign: 'center', my: 2 }}>
          <Typography 
            variant="h3" 
            sx={{ 
              fontWeight: 700,
              color: isPositive ? '#4caf50' : '#f44336',
              mb: 1
            }}
          >
            {formatCurrency(currentPnL)}
          </Typography>
          
          <Typography 
            variant="h5" 
            sx={{ 
              fontWeight: 600,
              color: pnlChangePercent >= 0 ? '#4caf50' : '#f44336'
            }}
          >
            {formatPercentage(pnlChangePercent)}
          </Typography>
        </Box>

        {/* Footer Info */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography 
              variant="caption" 
              sx={{ 
                color: 'rgba(255,255,255,0.8)'
              }}
            >
              {stats ? 'P&L Realizado' : 'Variação Diária'}
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: 600,
                color: (stats ? realizedPnL : pnlChange) >= 0 ? '#4caf50' : '#f44336'
              }}
            >
              {formatCurrency(stats ? realizedPnL : pnlChange)}
            </Typography>
          </Box>
          
          <Box sx={{ textAlign: 'right' }}>
            <Typography 
              variant="caption" 
              sx={{ 
                color: 'rgba(255,255,255,0.8)'
              }}
            >
              {stats ? 'P&L Não Realizado' : 'Status'}
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: 600,
                color: stats ? 
                  (unrealizedPnL >= 0 ? '#4caf50' : '#f44336') : 
                  (isPositive ? '#4caf50' : '#f44336')
              }}
            >
              {stats ? formatCurrency(unrealizedPnL) : (isPositive ? 'LUCRO' : 'PREJUÍZO')}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default PNLCard;