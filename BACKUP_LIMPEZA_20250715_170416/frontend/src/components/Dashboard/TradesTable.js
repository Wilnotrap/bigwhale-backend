// frontend/src/components/Dashboard/TradesTable.js
import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Typography,
  Box,
  Skeleton,
  useTheme,
  useMediaQuery,
  Card,
  CardContent,
  Grid,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Schedule,
  CheckCircle,
  Cancel
} from '@mui/icons-material';

const TradesTable = ({ trades, type, loading, hideValues = false }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [progress, setProgress] = useState(0);

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

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatCurrency = (value, isPrice = false) => {
    if (hideValues && !isPrice) return '$***'; // Preços não são ocultos
    if (value === null || value === undefined) return '$0.00';
    
    const numValue = parseFloat(value);
    
    // [CORREÇÃO] Ajustar casas decimais para melhor visualização
    if (isPrice) {
      // Para preços, usar 4 casas decimais
      return `$${numValue.toFixed(4)}`; 
    }

    // Para PNL e outros valores, usar 2 casas decimais
    return `$${numValue.toFixed(2)}`;
  };

  const formatPercentage = (value) => {
    // Percentuais permanecem visíveis
    if (value === null || value === undefined) return '0%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatSize = (value) => {
    if (hideValues) return '***';
    if (value === null || value === undefined) return '0';
    return parseFloat(value).toFixed(4);
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSideColor = (side) => {
    return side === 'buy' ? theme.palette.success.main : theme.palette.error.main;
  };

  const getSideIcon = (side) => {
    return side === 'buy' ? <TrendingUp /> : <TrendingDown />;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return 'primary';
      case 'closed':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'open':
        return <Schedule />;
      case 'closed':
        return <CheckCircle />;
      case 'cancelled':
        return <Cancel />;
      default:
        return null;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'open':
        return 'Aberto';
      case 'closed':
        return 'Fechado';
      case 'cancelled':
        return 'Cancelado';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <Box>
        {Array.from({ length: 5 }).map((_, index) => (
          <Box key={index} sx={{ mb: 1 }}>
            <Skeleton variant="rectangular" height={60} sx={{ borderRadius: 1 }} />
          </Box>
        ))}
      </Box>
    );
  }

  // Verificar se trades é um array
  if (!trades || !Array.isArray(trades) || trades.length === 0) {
    return (
      <Box
        sx={
          {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: 200,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`
          }
        }
      >
        <Typography variant="body1" color="text.secondary">
          {type === 'open' ? 'Nenhuma posição aberta' : 'Nenhum trade no histórico'}
        </Typography>
      </Box>
    );
  }

  const paginatedTrades = trades.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  // Versão mobile - Cards
  if (isMobile) {
    return (
      <Box>
        {/* Timer Visual para Mobile */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', mb: 2 }}>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
            Atualização automática
          </Typography>
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
              variant="determinate"
              value={progress}
              size={20}
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
              <Schedule sx={{ fontSize: 10, color: theme.palette.primary.main }} />
            </Box>
          </Box>
        </Box>
        <Grid container spacing={2}>
          {paginatedTrades.map((trade, index) => (
            <Grid item xs={12} key={trade.id || index}>
              <Card variant="outlined">
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                        {trade.symbol}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                        #{trade.id || trade.bitget_position_id || 'N/A'}
                      </Typography>
                      <Chip
                        icon={getSideIcon(trade.side)}
                        label={trade.side === 'buy' ? 'COMPRA' : 'VENDA'}
                        size="small"
                        sx={{
                          bgcolor: `${getSideColor(trade.side)}20`,
                          color: getSideColor(trade.side),
                          fontWeight: 'bold'
                        }}
                      />
                    </Box>
                    <Chip
                      icon={getStatusIcon(trade.status)}
                      label={getStatusText(trade.status)}
                      color={getStatusColor(trade.status)}
                      size="small"
                    />
                  </Box>

                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Preço de Abertura
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {formatCurrency(trade.entry_price, true)}
                      </Typography>
                    </Grid>
                    {trade.status === 'closed' && trade.exit_price && (
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Preço de Fechamento
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {formatCurrency(trade.exit_price, true)}
                        </Typography>
                      </Grid>
                    )}
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">
                        Abertura Moeda
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {formatSize(trade.size)}
                      </Typography>
                    </Grid>
                    {trade.status === 'closed' && (
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Fechamento Moeda
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {formatSize(trade.size)}
                        </Typography>
                      </Grid>
                    )}
                    {trade.pnl !== null && (
                      <Grid item xs={12}>
                        <Typography variant="caption" color="text.secondary">
                          Lucro / Prejuízo * Taxas Descontadas *
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 'bold',
                            color: trade.pnl >= 0 ? 'success.main' : 'error.main'
                          }}
                        >
                          {formatCurrency(trade.pnl)}
                        </Typography>
                      </Grid>
                    )}
                    <Grid item xs={12}>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="caption" color="text.secondary">
                        Hora e Data de Abertura: {formatDateTime(trade.created_at || trade.opened_at)}
                      </Typography>
                      {trade.closed_at && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          Hora e Data de Fechamento: {formatDateTime(trade.closed_at)}
                        </Typography>
                      )}
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <TablePagination
          component="div"
          count={trades.length}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Itens por página:"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
          sx={{ mt: 2 }}
        />
      </Box>
    );
  }

  // Versão desktop - Tabela
  return (
    <Box>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Moeda</TableCell>
              <TableCell>Lado</TableCell>
              <TableCell>Quantidade</TableCell>
              <TableCell>Preço de Abertura</TableCell>
              {type === 'closed' && <TableCell>Preço de Fechamento</TableCell>}
              <TableCell>P&L</TableCell>
              <TableCell>Data de Abertura</TableCell>
              {type === 'closed' && <TableCell>Data de Fechamento</TableCell>}
              <TableCell>Ordem ID</TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Status
                  {/* Timer Visual de 30s */}
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <CircularProgress
                      variant="determinate"
                      value={progress}
                      size={20}
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
                      <Schedule sx={{ fontSize: 10, color: theme.palette.primary.main }} />
                    </Box>
                  </Box>
                </Box>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedTrades.map((trade, index) => (
              <TableRow key={trade.id || index} hover>
                {/* Moeda (Symbol) */}
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {trade.symbol}
                  </Typography>
                </TableCell>
                
                {/* Lado (holdside/side) */}
                <TableCell>
                  <Chip
                    icon={getSideIcon(trade.side)}
                    label={trade.side === 'buy' ? 'COMPRA' : 'VENDA'}
                    size="small"
                    sx={{
                      bgcolor: `${getSideColor(trade.side)}20`,
                      color: getSideColor(trade.side),
                      fontWeight: 'bold'
                    }}
                  />
                </TableCell>
                
                {/* Quantidade (size) */}
                <TableCell align="right">{formatSize(trade.size)}</TableCell>
                
                {/* Preço de Abertura (entry_price) */}
                <TableCell align="right">{formatCurrency(trade.entry_price, true)}</TableCell>
                
                {/* Preço de Fechamento (exit_price) - apenas para trades fechados */}
                {type === 'closed' && (
                  <TableCell align="right">
                    {trade.exit_price !== null && trade.exit_price !== undefined ? formatCurrency(trade.exit_price, true) : 'N/A'}
                  </TableCell>
                )}
                
                {/* P&L (pnl) */}
                <TableCell align="right">
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 'bold',
                      color: trade.pnl >= 0 ? 'success.main' : 'error.main'
                    }}
                  >
                    {trade.pnl !== null ? formatCurrency(trade.pnl) : '-'}
                  </Typography>
                </TableCell>
                
                {/* Data de Abertura (created_at) */}
                <TableCell>
                  <Typography variant="caption" color="text.secondary">
                    {formatDateTime(trade.created_at || trade.opened_at)}
                  </Typography>
                </TableCell>
                
                {/* Data de Fechamento (closed_at) - apenas para trades fechados */}
                {type === 'closed' && (
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {trade.closed_at ? formatDateTime(trade.closed_at) : 'N/A'}
                    </Typography>
                  </TableCell>
                )}
                
                {/* Ordem ID (id) */}
                <TableCell>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                    #{trade.id || trade.bitget_position_id || 'N/A'}
                  </Typography>
                </TableCell>
                
                {/* Status */}
                <TableCell>
                  <Chip
                    icon={getStatusIcon(trade.status)}
                    label={getStatusText(trade.status)}
                    color={getStatusColor(trade.status)}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={trades.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="Itens por página:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
      />
    </Box>
  );
};

export default TradesTable;