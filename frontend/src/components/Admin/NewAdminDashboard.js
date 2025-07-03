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
  useTheme,
  useMediaQuery,
  Tooltip,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Paper
} from '@mui/material';
import {
  AccountCircle,
  Logout,
  Refresh,
  TrendingUp,
  TrendingDown,
  AccountBalance,
  ShowChart,
  Timeline,
  Percent,
  Receipt,
  ArrowBack
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-toastify';
import API_CONFIG from '../../config/api';

const NewAdminDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [anchorEl, setAnchorEl] = useState(null);
  const [stats, setStats] = useState(null);
  const [positions, setPositions] = useState([]);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
    
    // Auto-refresh a cada 30 segundos
    const interval = setInterval(() => {
      loadDashboardData(true);
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async (silent = false) => {
    if (!silent) setLoading(true);
    if (silent) setRefreshing(true);
    
    try {
      const [statsResponse, positionsResponse, balanceResponse] = await Promise.all([
        fetch(`${API_CONFIG.baseURL}/api/admin/dashboard/consolidated-stats`, {
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        }),
        fetch(`${API_CONFIG.baseURL}/api/admin/dashboard/consolidated-positions`, {
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        }),
        fetch(`${API_CONFIG.baseURL}/api/admin/dashboard/consolidated-balance`, {
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' }
        })
      ]);

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData.data);
      }

      if (positionsResponse.ok) {
        const positionsData = await positionsResponse.json();
        setPositions(positionsData.data || []);
      }

      if (balanceResponse.ok) {
        const balanceData = await balanceResponse.json();
        setBalance(balanceData.balance);
      }

    } catch (error) {
      console.error('Erro ao carregar dados do dashboard admin:', error);
      toast.error('Erro ao carregar dados do dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
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

  const handleRefresh = () => {
    loadDashboardData();
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatPercentage = (value) => {
    const color = value >= 0 ? '#4caf50' : '#f44336';
    return (
      <span style={{ color }}>
        {value >= 0 ? '+' : ''}{value?.toFixed(2)}%
      </span>
    );
  };

  const StatCard = ({ title, value, secondaryValue, icon, color = 'primary' }) => (
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

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Barra Superior */}
      <AppBar position="static" color="transparent" elevation={0}>
        <Toolbar>
          <IconButton onClick={() => navigate('/admin')} sx={{ mr: 2 }}>
            <ArrowBack />
          </IconButton>
          <Typography variant="subtitle1" component="div" sx={{ flexGrow: 1, fontSize: '1.25rem', fontWeight: 600 }}>
            Dashboard Consolidado - Administração
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Atualizar dados">
              <span>
                <IconButton onClick={handleRefresh} disabled={refreshing}>
                  {refreshing ? <CircularProgress size={24} /> : <Refresh />}
                </IconButton>
              </span>
            </Tooltip>

            <IconButton
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user?.full_name?.charAt(0) || 'A'}
              </Avatar>
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleLogout}>
                <Logout sx={{ mr: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        {/* Cards de Estatísticas */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Saldo Total"
              value={formatCurrency(balance?.total_balance)}
              secondaryValue={`${balance?.active_apis || 0} APIs ativas`}
              icon={<AccountBalance sx={{ color: '#4caf50' }} />}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="PnL Total"
              value={formatCurrency(stats?.pnl_total)}
              secondaryValue={formatPercentage(stats?.win_rate)}
              icon={<ShowChart sx={{ color: stats?.pnl_total >= 0 ? '#4caf50' : '#f44336' }} />}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total de Trades"
              value={stats?.total_trades || 0}
              secondaryValue={`${stats?.win_rate?.toFixed(1) || 0}% win rate`}
              icon={<Receipt sx={{ color: '#2196f3' }} />}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Posições Abertas"
              value={stats?.open_positions || 0}
              secondaryValue={formatCurrency(balance?.unrealized_pnl)}
              icon={<Timeline sx={{ color: '#ff9800' }} />}
            />
          </Grid>
        </Grid>

        {/* Tabela de Posições Abertas */}
        <Paper sx={{ p: 2, backgroundColor: '#1C2127', color: 'white' }}>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <Timeline sx={{ mr: 1 }} />
            Posições Abertas Consolidadas
          </Typography>
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : positions.length === 0 ? (
            <Typography sx={{ textAlign: 'center', p: 3, color: 'rgba(255, 255, 255, 0.7)' }}>
              Nenhuma posição aberta encontrada
            </Typography>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Usuário</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Símbolo</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Lado</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Tamanho</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Alavancagem</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Preço Entrada</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Preço Atual</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>PnL</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>ROE</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {positions.map((position, index) => (
                    <TableRow key={index}>
                      <TableCell sx={{ color: 'white' }}>
                        {position.user_name}
                      </TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>
                        {position.symbol}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={position.side?.toUpperCase()}
                          color={position.side === 'long' ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {position.size?.toFixed(4)}
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {position.leverage}x
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {formatCurrency(position.entry_price)}
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>
                        {formatCurrency(position.mark_price)}
                      </TableCell>
                      <TableCell sx={{ color: position.unrealized_pnl >= 0 ? '#4caf50' : '#f44336' }}>
                        {formatCurrency(position.unrealized_pnl)}
                      </TableCell>
                      <TableCell sx={{ color: position.roe >= 0 ? '#4caf50' : '#f44336' }}>
                        {formatPercentage(position.roe)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default NewAdminDashboard;