import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  Box,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Close,
  Refresh
} from '@mui/icons-material';
import dashboardService from '../../services/dashboardService';
import TradesTable from './TradesTable';

const ClosedTradesModal = ({ open, onClose, hideValues = false }) => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const loadClosedTrades = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await dashboardService.getClosedTrades();
      console.log('Resposta do backend (trades fechados):', response);
      
      if (response.success) {
        setTrades(response.data || []);
      } else {
        setError(response.message || 'Erro ao carregar trades fechados');
      }
    } catch (err) {
      console.error('Erro ao carregar trades fechados:', err);
      setError('Erro ao carregar trades fechados');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadClosedTrades();
    setRefreshing(false);
  };

  useEffect(() => {
    if (open) {
      loadClosedTrades();
    }
  }, [open]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xl"
      fullWidth
      PaperProps={{
        sx: {
          height: '90vh',
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Trades Fechados</Typography>
          <Box>
            <Tooltip title="Atualizar">
              <IconButton onClick={handleRefresh} disabled={refreshing}>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Fechar">
              <IconButton onClick={onClose}>
                <Close />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 2, height: '100%', overflow: 'hidden' }}>
        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        ) : trades.length === 0 ? (
          <Alert severity="info">Nenhum trade fechado encontrado</Alert>
        ) : (
          <Box sx={{ height: '100%', overflow: 'auto' }}>
            <TradesTable 
              trades={trades} 
              type="closed" 
              loading={false} 
              hideValues={hideValues} 
            />
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ClosedTradesModal;