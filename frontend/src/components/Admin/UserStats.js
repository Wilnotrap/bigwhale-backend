import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container, Typography, Box, Card, CardContent, Grid,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, IconButton, AppBar, Toolbar, CircularProgress,
  Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import {
  ArrowBack, TrendingUp, TrendingDown, ExpandMore,
  ShowChart, AttachMoney, BarChart, Timeline, Analytics,
  AccountBalance, PeopleAlt, Assessment
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import API_CONFIG from '../../config/api';

const UserStats = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUserStats();
  }, [userId]);

  const fetchUserStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_CONFIG.baseURL}/api/admin/user/${userId}/stats/detailed`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
        setUser(data.user);
      } else {
        toast.error('Erro ao carregar estatísticas do usuário.');
      }
    } catch (error) {
      toast.error('Erro ao carregar estatísticas.');
    } finally {
      setLoading(false);
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
            Estatísticas Detalhadas - {user?.full_name || 'Usuário'}
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        {stats && (
          <Grid container spacing={3}>
            {/* Estatísticas Básicas */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Estatísticas Básicas
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={3}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="primary">
                          {stats.basic?.total_trades || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total de Trades
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Box textAlign="center">
                        <Typography variant="h4" sx={{ color: getPnlColor(stats.basic?.total_pnl) }}>
                          {formatUsd(stats.basic?.total_pnl)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          PnL Total
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="success.main">
                          {stats.basic?.winning_trades || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Trades Vencedores
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="info.main">
                          {formatPercentage(stats.basic?.win_rate)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Taxa de Vitória
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Estatísticas por Símbolo */}
            <Grid item xs={12} md={6}>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">
                    <ShowChart sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Estatísticas por Símbolo
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Símbolo</TableCell>
                          <TableCell align="right">Trades</TableCell>
                          <TableCell align="right">PnL</TableCell>
                          <TableCell align="right">Taxa Vitória</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {stats.by_symbol?.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>{item.symbol}</TableCell>
                            <TableCell align="right">{item.trade_count}</TableCell>
                            <TableCell align="right">
                              <Typography sx={{ color: getPnlColor(item.total_pnl) }}>
                                {formatUsd(item.total_pnl)}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              {formatPercentage(item.win_rate)}
                            </TableCell>
                          </TableRow>
                        )) || []}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Estatísticas por Lado (Long/Short) */}
            <Grid item xs={12} md={6}>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">
                    <BarChart sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Estatísticas por Lado
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Lado</TableCell>
                          <TableCell align="right">Trades</TableCell>
                          <TableCell align="right">PnL</TableCell>
                          <TableCell align="right">Taxa Vitória</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {stats.by_side?.map((item, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Chip
                                label={getSideText(item.side)}
                                size="small"
                                sx={{
                                  backgroundColor: getSideColor(item.side),
                                  color: 'white',
                                  fontWeight: 'bold'
                                }}
                              />
                            </TableCell>
                            <TableCell align="right">{item.trade_count}</TableCell>
                            <TableCell align="right">
                              <Typography sx={{ color: getPnlColor(item.total_pnl) }}>
                                {formatUsd(item.total_pnl)}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              {formatPercentage(item.win_rate)}
                            </TableCell>
                          </TableRow>
                        )) || []}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Últimos 10 Trades */}
            <Grid item xs={12}>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">
                    <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Últimos 10 Trades
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Símbolo</TableCell>
                          <TableCell>Lado</TableCell>
                          <TableCell align="right">Preço Entrada</TableCell>
                          <TableCell align="right">Preço Saída</TableCell>
                          <TableCell align="right">PnL</TableCell>
                          <TableCell align="right">ROE</TableCell>
                          <TableCell>Data</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {stats.recent_trades?.map((trade, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Typography variant="body2" fontWeight="bold">
                                {trade.symbol}
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
                            <TableCell align="right">
                              {formatUsd(trade.entry_price)}
                            </TableCell>
                            <TableCell align="right">
                              {trade.exit_price ? formatUsd(trade.exit_price) : '-'}
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
                          </TableRow>
                        )) || []}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        )}
      </Container>
    </Box>
  );
};

export default UserStats;