// frontend/src/components/Dashboard/CommissionBalanceCard.js
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Skeleton,
  Chip,
  useTheme,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  AccountBalanceWallet,
  Refresh,
  TrendingUp,
  TrendingDown,
  Info
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import API_CONFIG from '../../config/api';

const CommissionBalanceCard = ({ hideValues = false }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [balanceData, setBalanceData] = useState({
    available: 0,
    used: 0,
    total: 0,
    lastUpdate: null
  });

  const fetchCommissionBalance = async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
    }
    try {
      const response = await fetch(`${API_CONFIG.baseURL}/api/dashboard/stats`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Erro ao buscar dados');
      }
      
      const result = await response.json();
      
      if (result.success && result.data) {
        const stats = result.data;
        
        // Calcular valores usados baseado na porcentagem
        const totalUsd = stats.operational_balance_usd || 0;
        const totalBrl = stats.operational_balance || 0;
        const usagePercentage = stats.operational_balance_percentage || 0;
        
        const usedUsd = (totalUsd * usagePercentage) / 100;
        const usedBrl = (totalBrl * usagePercentage) / 100;
        const availableUsd = totalUsd - usedUsd;
        const availableBrl = totalBrl - usedBrl;
        
        setBalanceData({
          available: availableBrl,
          used: usedBrl,
          total: totalBrl,
          availableUsd: availableUsd,
          usedUsd: usedUsd,
          totalUsd: totalUsd,
          lastUpdate: new Date()
        });
      } else {
        throw new Error('Dados inválidos recebidos');
      }
      
    } catch (error) {
      console.error('Erro ao buscar saldo de comissão:', error);
      toast.error('Erro ao carregar saldo de comissão');
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchCommissionBalance(true); // Primeira carga com loading
  }, []);

  const formatCurrency = (value) => {
    if (hideValues) return '$***';
    if (value === null || value === undefined) return '$0.00';
    return `$${parseFloat(value).toFixed(2)}`;
  };

  const getUsagePercentage = () => {
    if (balanceData.totalUsd === 0) return 0;
    return (balanceData.usedUsd / balanceData.totalUsd) * 100;
  };

  const getUsageColor = () => {
    const percentage = getUsagePercentage();
    if (percentage < 30) return '#4caf50'; // Verde
    if (percentage < 70) return '#ff9800'; // Laranja
    return '#f44336'; // Vermelho
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)'
        }
      }}
    >
      <CardContent sx={{ 
        p: 1.5, 
        '&:last-child': { pb: 1.5 },
        minHeight: '180px',
        maxHeight: '180px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          mb: 0.5
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <AccountBalanceWallet sx={{ fontSize: 32, opacity: 0.9 }} />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              Saldo Comissão
            </Typography>
          </Box>
          <Tooltip title="Atualizar saldo">
            <span>
              <IconButton 
                onClick={fetchCommissionBalance}
                disabled={loading}
                sx={{ 
                  color: 'white', 
                  opacity: 0.8,
                  '&:hover': { opacity: 1 }
                }}
              >
                <Refresh sx={{ fontSize: 20 }} />
              </IconButton>
            </span>
          </Tooltip>
        </Box>
        
        {loading ? (
          <Box>
            <Skeleton variant="text" width="60%" sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
            <Skeleton variant="text" width="40%" sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
            <Skeleton variant="text" width="80%" sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
          </Box>
        ) : (
          <>
            {/* Saldo Disponível */}
            <Box sx={{ mb: 0.3 }}>
              <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.1, fontSize: '0.7rem' }}>
                Saldo Disponível
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 0.1, fontSize: '1.1rem' }}>
                {hideValues ? '••••••' : `$${balanceData.availableUsd.toFixed(2)}`}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8, fontSize: '0.7rem' }}>
                R$ {hideValues ? '••••••' : balanceData.available.toFixed(2)}
              </Typography>
            </Box>
            
            {/* Estatísticas */}
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 0.3
            }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ opacity: 0.8, fontSize: '0.65rem' }}>
                  Usado
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                  ${hideValues ? '••••••' : balanceData.usedUsd.toFixed(2)}
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.7, fontSize: '0.6rem' }}>
                  R$ {hideValues ? '••••••' : balanceData.used.toFixed(2)}
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ opacity: 0.8, fontSize: '0.65rem' }}>
                  Total
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                  ${hideValues ? '••••••' : balanceData.totalUsd.toFixed(2)}
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.7, fontSize: '0.6rem' }}>
                  R$ {hideValues ? '••••••' : balanceData.total.toFixed(2)}
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ opacity: 0.8, fontSize: '0.65rem' }}>
                  Uso
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                  {getUsagePercentage().toFixed(1)}%
                </Typography>
              </Box>
            </Box>
            
            {/* Barra de Progresso */}
            <Box sx={{ mb: 0.5 }}>
              <Box sx={{ 
                width: '100%', 
                height: 4, 
                bgcolor: 'rgba(255,255,255,0.2)', 
                borderRadius: 2,
                overflow: 'hidden'
              }}>
                <Box sx={{ 
                  width: `${getUsagePercentage()}%`, 
                  height: '100%', 
                  bgcolor: getUsageColor(),
                  transition: 'width 0.3s ease'
                }} />
              </Box>
            </Box>
            
            {/* Status e Informações */}
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              mt: 0.5
            }}>
              <Chip
                size="small"
                label={getUsagePercentage() < 70 ? 'Saudável' : getUsagePercentage() < 90 ? 'Atenção' : 'Crítico'}
                sx={{
                  bgcolor: getUsageColor(),
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.6rem',
                  height: '20px'
                }}
              />
              
              {balanceData.lastUpdate && (
                <Typography variant="caption" sx={{ opacity: 0.7, fontSize: '0.6rem' }}>
                  Atualizado: {balanceData.lastUpdate.toLocaleTimeString('pt-BR', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </Typography>
              )}
            </Box>
            
            {/* Informação Adicional */}
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 0.5,
              mt: 0.5,
              pt: 0.5,
              borderTop: '1px solid rgba(255,255,255,0.2)'
            }}>
              <Info sx={{ fontSize: 12, opacity: 0.8 }} />
              <Typography variant="body2" sx={{ opacity: 0.8, fontSize: '0.65rem' }}>
                Usado para cobrir taxas de trading
              </Typography>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default CommissionBalanceCard;