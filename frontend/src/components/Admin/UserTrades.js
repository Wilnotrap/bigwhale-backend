import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container, Typography, Box, Card, CardContent, Grid,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, IconButton, TextField, InputAdornment, Select, MenuItem,
  FormControl, InputLabel, Tooltip, AppBar, Toolbar, Button,
  Pagination, CircularProgress
} from '@mui/material';
import {
  ArrowBack, Search, FilterList, TrendingUp, TrendingDown,
  Close, Visibility, ShowChart, AttachMoney, BarChart,
  Timeline, Analytics
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import API_CONFIG from '../../config/api';

const UserTrades = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [symbolFilter, setSymbolFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [symbols, setSymbols] = useState([]);

  useEffect(() => {
    fetchUserTrades();
  }, [userId, page, statusFilter, symbolFilter, searchTerm]);

  const fetchUserTrades = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '20'
      });
      
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (symbolFilter !== 'all') params.append('symbol', symbolFilter);
      if (searchTerm) params.append('search', searchTerm);

      const response = await fetch(`${API_CONFIG.baseURL}/api/admin/user/${userId}/trades?${params}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setTrades(data.trades || []);
        setUser(data.user);
        setTotalPages(data.total_pages || 1);
        
        // Extrair símbolos únicos
        const uniqueSymbols = [...new Set(data.trades?.map(trade => trade.symbol) || [])];
        setSymbols(uniqueSymbols);
      } else {
        toast.error('Erro ao carregar trades do usuário.');
      }
    } catch (error) {
      toast.error('Erro ao carregar trades.');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseTrade = async (tradeId) => {
    try {
      const response = await fetch(`${API_CONFIG.baseURL}/api/admin/trades/${tradeId}/close`, {
        method: 'POST',
        credentials: 'include'
      });

      const data = await response.json();
      if (response.ok) {
        toast.success(data.message);
        fetchUserTrades();
      } else {
        toast.error(data.message);
      }
    } catch (error) {
      toast.error('Erro ao fechar trade.');
    }
  };

  const formatUsd = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'primary';
      case 'closed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'open': return 'Aberto';
      case 'closed': return 'Fechado';
      case 'cancelled': return 'Cancelado';
      default: return status;
    }
  };

  const getPnlColor = (pnl) => {
    if (pnl > 0) return 'success.main';
    if (pnl < 0) return 'error.main';
    return 'text.primary';
  };

  const getSideColor = (side) => {
    return side === 'long' ? 'success.main' : 'error.main';
  };

  const getSideText = (side) => {
    return side === 'long' ? 'LONG' : 'SHORT';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/admin')}
            sx={{ mr: 2 }}
          >
            <ArrowBack />
          </IconButton>
          <Typography variant="subtitle1" component="div" sx={{ flexGrow: 1, fontSize: '1.25rem', fontWeight: 600 }}>
            Trades de {user?.full_name || 'Usuário'}
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        {/* Filtros */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  placeholder="Buscar por símbolo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={statusFilter}
                    label="Status"
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <MenuItem value="all">Todos</MenuItem>
                    <MenuItem value="open">Abertos</MenuItem>
                    <MenuItem value="closed">Fechados</MenuItem>
                    <MenuItem value="cancelled">Cancelados</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Símbolo</InputLabel>
                  <Select
                    value={symbolFilter}
                    label="Símbolo"
                    onChange={(e) => setSymbolFilter(e.target.value)}
                  >
                    <MenuItem value="all">Todos</MenuItem>
                    {symbols.map((symbol) => (
                      <MenuItem key={symbol} value={symbol}>
                        {symbol}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('all');
                    setSymbolFilter('all');
                    setPage(1);
                  }}
                >
                  Limpar Filtros
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Tabela de Trades */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Símbolo</TableCell>
                  <TableCell>Lado</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Preço Entrada</TableCell>
                  <TableCell align="right">Preço Saída</TableCell>
                  <TableCell align="right">Quantidade</TableCell>
                  <TableCell align="right">PnL</TableCell>
                  <TableCell align="right">ROE</TableCell>
                  <TableCell>Data Abertura</TableCell>
                  <TableCell>Data Fechamento</TableCell>
                  <TableCell align="center">Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {trades.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={11} align="center">
                      <Typography variant="body2" color="text.secondary">
                        Nenhum trade encontrado
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  trades.map((trade) => (
                    <TableRow key={trade.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {trade.symbol}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {trade.leverage ? `${trade.leverage}x` : '50x'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getSideText(trade.side)}
                          size="small"
                          sx={{
                            backgroundColor: getSideColor(trade.side),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusText(trade.status)}
                          size="small"
                          color={getStatusColor(trade.status)}
                        />
                      </TableCell>
                      <TableCell align="right">
                        {formatUsd(trade.entry_price)}
                      </TableCell>
                      <TableCell align="right">
                        {trade.exit_price ? formatUsd(trade.exit_price) : '-'}
                      </TableCell>
                      <TableCell align="right">
                        {trade.quantity}
                      </TableCell>
                      <TableCell align="right">
                        <Typography sx={{ color: getPnlColor(trade.pnl) }}>
                          {formatUsd(trade.pnl)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography sx={{ color: getPnlColor(trade.roe) }}>
                          {formatPercentage(trade.roe)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {formatDate(trade.created_at)}
                      </TableCell>
                      <TableCell>
                        {trade.closed_at ? formatDate(trade.closed_at) : '-'}
                      </TableCell>
                      <TableCell align="center">
                        {trade.status === 'open' && (
                          <Tooltip title="Fechar Trade">
                            <IconButton
                              size="small"
                              onClick={() => handleCloseTrade(trade.id)}
                              sx={{ color: 'error.main' }}
                            >
                              <Close />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Paginação */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(event, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default UserTrades;