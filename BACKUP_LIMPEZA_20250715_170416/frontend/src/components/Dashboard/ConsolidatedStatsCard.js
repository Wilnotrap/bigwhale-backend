import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Skeleton,
  useTheme,
  Divider,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Collapse,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ShowChart,
  Timeline,
  TrendingUp,
  FilterList,
  ExpandMore,
  ExpandLess,
  InfoOutlined
} from '@mui/icons-material';
import dashboardService from '../../services/dashboardService';
import { formatCurrency, formatPercentage, getColorByValue } from '../../utils/formatters';

const ConsolidatedStatsCard = ({ hideValues = false }) => {
  const theme = useTheme();
  const [stats, setStats] = useState({
    realized_pnl: 0,
    unrealized_pnl: 0,
    total_pnl: 0,
    win_rate: 0,
    total_trades: 0,
    winning_trades: 0,
    open_positions_count: 0,
    margin_size: 0,
  });
  const [openPositions, setOpenPositions] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [initialLoad, setInitialLoad] = useState(true);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [filterDates, setFilterDates] = useState({ startDate: '', endDate: '' });

  // Carregar dados do dashboard
  useEffect(() => {
    const loadStats = async (showLoading = true) => {
      try {
        if (showLoading && initialLoad) {
          setLoading(true);
        }
        
        // A rota /stats agora é a única fonte da verdade, buscando tudo da Bitget.
        const response = await dashboardService.getUserStats(filterDates.startDate, filterDates.endDate);
        
        const statsData = response.data || response;
        
        if (statsData) {
          setStats(statsData);
        } else {
          // Reinicia os stats em caso de resposta inesperada
          setStats({
            realized_pnl: 0, unrealized_pnl: 0, total_pnl: 0, win_rate: 0,
            total_trades: 0, winning_trades: 0, open_positions_count: 0, margin_size: 0
          });
        }
        
        // Carregar posições abertas para cálculo do ROE Ponderado customizado
        const openPosResp = await dashboardService.getOpenPositions();
        setOpenPositions(openPosResp.data || []);
        
        if (initialLoad) {
          setInitialLoad(false);
        }
      } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        // Mantém os stats zerados em caso de erro
        setStats({
          realized_pnl: 0, unrealized_pnl: 0, total_pnl: 0, win_rate: 0,
          total_trades: 0, winning_trades: 0, open_positions_count: 0, margin_size: 0
        });
        setOpenPositions([]);
      } finally {
        if (showLoading && initialLoad) {
          setLoading(false);
        }
      }
    };

    loadStats(initialLoad);
    
    // Timer para atualização automática a cada 30 segundos
    const interval = setInterval(() => {
        loadStats(false);
    }, 30000);
    
    return () => clearInterval(interval);
  }, [filterDates.startDate, filterDates.endDate, initialLoad]);

  // Função para limpar filtros
  const clearFilters = () => {
    setFilterDates({ startDate: '', endDate: '' });
  };

  // Funções de formatação agora são importadas de utils/formatters.js para garantir consistência

  // Usar dados das estatísticas do backend (que já calculam baseado na Bitget)
  const getRealizedProfit = () => {
    return stats?.realized_pnl || 0;
  };

  // Usar taxa de acerto das estatísticas do backend
  const getWinRate = () => {
    return stats?.win_rate || 0;
  };

  // Novo cálculo do ROE Ponderado baseado nas posições abertas
  const calculateOpenROE = () => {
    console.log('Posições abertas para cálculo do ROE:', openPositions);
    if (!openPositions || openPositions.length === 0) return null;
    
    // Para múltiplas posições, calcular ROE ponderado pela margem
    let totalUnrealizedPnl = 0;
    let totalMargin = 0;
    
    openPositions.forEach(pos => {
      const unrealized = parseFloat(pos.unrealized_pnl || 0);
      const margin = parseFloat(pos.margin_size || 0);
      
      if (margin > 0) {
        totalUnrealizedPnl += unrealized;
        totalMargin += margin;
      }
    });
    
    if (totalMargin === 0) return 0;
    
    // ROE total = (PnL total não realizado / margem total) * 100
    return (totalUnrealizedPnl / totalMargin) * 100;
  };

  const realizedProfit = getRealizedProfit();
  const winRate = getWinRate();
  const openROE = calculateOpenROE();
  
  // Debug: verificar dados carregados
  console.log('Stats from backend:', stats);
  console.log('Realized profit from stats:', realizedProfit);
  console.log('Win rate from stats:', winRate);

  if (loading) {
    return (
      <Paper sx={{ p: 2.5, height: 320 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          📊 Estatísticas de Trading
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="rectangular" height={60} />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2.5, height: 'auto', minHeight: 320, transition: 'all 0.3s ease-in-out' }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '1.1rem' }}>
          📊 Estatísticas de Trading
        </Typography>
        <IconButton 
          onClick={() => setIsFilterOpen(!isFilterOpen)}
          size="small"
          sx={{ color: theme.palette.primary.main }}
        >
          <FilterList />
          {isFilterOpen ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      </Box>

      {/* Filtros de Data */}
      <Collapse in={isFilterOpen}>
        <Card sx={{ mb: 2, bgcolor: 'background.default' }}>
          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Grid container spacing={1.5}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Data Inicial"
                  type="date"
                  value={filterDates.startDate}
                  onChange={(e) => setFilterDates({ ...filterDates, startDate: e.target.value })}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Data Final"
                  type="date"
                  value={filterDates.endDate}
                  onChange={(e) => setFilterDates({ ...filterDates, endDate: e.target.value })}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  fullWidth
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  variant="outlined"
                  onClick={clearFilters}
                  fullWidth
                  size="small"
                >
                  Limpar Filtros
                </Button>
              </Grid>
            </Grid>
            <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
              * Sem filtro = mês atual. Com filtro = período personalizado para o Lucro Realizado.
            </Typography>
          </CardContent>
        </Card>
      </Collapse>

      {/* Conteúdo */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        
        {/* Lucro Realizado */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          p: 1.5,
          bgcolor: 'background.default',
          borderRadius: 1,
          border: `1px solid ${theme.palette.divider}`
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Timeline sx={{ color: getColorByValue(realizedProfit), fontSize: 20 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              Lucro Realizado
            </Typography>
          </Box>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 'bold',
              color: getColorByValue(realizedProfit)
            }}
          >
            {realizedProfit >= 0 ? '+' : ''}{formatCurrency(realizedProfit, true, hideValues)}
          </Typography>
        </Box>

        <Divider sx={{ my: 0.5 }} />

        {/* ROE Ponderado */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          p: 1.5,
          bgcolor: 'background.default',
          borderRadius: 1,
          border: `1px solid ${theme.palette.divider}`
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <TrendingUp sx={{ color: getColorByValue(openROE), fontSize: 20 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              ROE Ponderado
            </Typography>
            <Tooltip title={
              <>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>ROE da Operação:</Typography>
                <Typography variant="body2">É o lucro/prejuízo em porcentagem sobre o capital específico daquela operação.</Typography>
                <br/>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>ROE Ponderado:</Typography>
                <Typography variant="body2">É o lucro/prejuízo em porcentagem sobre o capital total da sua conta, considerando o peso de cada operação. Ele é uma média mais realista do desempenho do seu portfólio como um todo, pois entende que um pequeno ganho em uma operação grande (muita margem) pode ser mais impactante no seu patrimônio do que um grande ganho em uma operação pequena (pouca margem).</Typography>
              </>
            }>
              <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                <InfoOutlined fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: getColorByValue(openROE || 0) }}>
            {openROE === null ? "Sem posições abertas" : formatPercentage(openROE, false)}
          </Typography>
        </Box>

        <Divider sx={{ my: 0.5 }} />

        {/* Taxa de Acerto */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          p: 1.5,
          bgcolor: 'background.default',
          borderRadius: 1,
          border: `1px solid ${theme.palette.divider}`
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUp sx={{ color: getColorByValue(winRate), fontSize: 20 }} />
            <Typography variant="body1" sx={{ fontWeight: 500 }}>
              Taxa de Acerto
            </Typography>
          </Box>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 'bold',
              color: getColorByValue(winRate)
            }}
          >
            {formatPercentage(winRate, false)}
          </Typography>
        </Box>

        {/* Informação adicional */}
        <Box sx={{ mt: 'auto', pt: 1 }}>
          <Typography variant="caption" color="text.secondary" align="center" display="block">
            Atualizado automaticamente a cada 30 segundos
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default ConsolidatedStatsCard;