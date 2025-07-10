import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Button,
  TextField,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Close,
  Refresh
} from '@mui/icons-material';
import dashboardService from '../../services/dashboardService';
import logger from '../../utils/logger';
import { toast } from 'react-hot-toast';
import { formatValue, formatDateTime, getColorByValue } from '../../utils/formatters';

const FinishedOperationsModal = ({ open, onClose, hideValues = false }) => {
  const [positions, setPositions] = useState([]);
  const [filteredPositions, setFilteredPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [totalCommissions, setTotalCommissions] = useState(0);

  const loadFinishedPositions = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      console.log('Carregando operações finalizadas com filtros:', { startDate, endDate });
      
      // Buscar posições com filtros de data aplicados no backend (mesmo sistema das estatísticas)
      const response = await dashboardService.getFinishedPositions(startDate, endDate);
      console.log('Resposta completa da API:', response);
      
      if (response && response.success) {
        const positionsData = response.positions || [];
        console.log('Posições encontradas (já filtradas pelo backend):', positionsData);
        console.log('Filtros aplicados:', response.filters_applied);
        
        // Ordenar por data de fechamento (utime) - mais recentes primeiro
        const sortedData = positionsData.sort((a, b) => {
          const timeA = parseInt(a.utime) || 0;
          const timeB = parseInt(b.utime) || 0;
          return timeB - timeA;
        });
        
        // Como os dados já vêm filtrados do backend, usar diretamente
        setPositions(sortedData);
        setFilteredPositions(sortedData);
        calculateTotalCommissions(sortedData);
        
        console.log(`${sortedData.length} operações finalizadas carregadas (já filtradas pelo backend)`);
        
        if (sortedData.length === 0) {
          if (startDate || endDate) {
            setError('Nenhuma operação encontrada no período selecionado');
          } else {
            setError('Nenhuma operação finalizada encontrada');
          }
        }
      } else {
        const errorMessage = response?.message || 'Erro ao carregar operações encerradas';
        setError(errorMessage);
        console.error('Erro na resposta:', errorMessage);
      }
    } catch (err) {
      const errorMessage = err.message || 'Erro ao carregar operações encerradas';
      setError(errorMessage);
      logger.error(errorMessage, err);
      toast.error(errorMessage);
      console.error('Erro ao carregar operações:', err);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    if (open) {
      loadFinishedPositions();
    }
  }, [open, loadFinishedPositions]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadFinishedPositions();
    setRefreshing(false);
  };

  // Funções de formatação agora são importadas de utils/formatters.js para garantir consistência

     // Função para traduzir os títulos das colunas
   const getColumnTitle = (key) => {
     const translations = {
       'symbol': 'Par',
       'openAvgPrice': 'Preço de Abertura',
       'closeAvgPrice': 'Preço de Fechamento',
       'holdSide': 'Lado',
       'openTotalPos': 'Tamanho Abertura',
       'closeTotalPos': 'Tamanho Fechamento',
       'pnl': 'Lucro / Prejuízo',
       'marginMode': 'Modo Margem',
       'ctime': 'Data Abertura',
       'utime': 'Data Fechamento',
       'positionId': 'ID da Posição',
       'comissao': 'Comissão',
       'leverage': 'Alavancagem',
       'netProfit': 'Lucro Líquido',
       'marginCoin': 'Moeda Margem',
       'openFee': 'Taxa Abertura',
       'closeFee': 'Taxa Fechamento',
       'totalFunding': 'Funding Total'
     };
     return translations[key] || key;
   };

   // Função para traduzir valores específicos
   const translateValue = (key, value) => {
     if (key === 'marginMode') {
       const marginModeTranslations = {
         'crossed': 'Cruzada',
         'isolated': 'Isolada'
       };
       return marginModeTranslations[value] || value;
     }
     return value;
   };

  // Função para obter todas as chaves únicas dos objetos com ordem personalizada
  const getAllKeys = (data) => {
    if (!Array.isArray(data) || data.length === 0) return [];
    const keys = new Set();
    data.forEach(item => {
      Object.keys(item).forEach(key => keys.add(key));
    });
    
    // Ordem personalizada das colunas com os campos importantes da API da Bitget
    const priorityOrder = [
      'symbol',
      'holdSide',
      'leverage',
      'openAvgPrice',
      'closeAvgPrice', 
      'openTotalPos',
      'closeTotalPos',
      'pnl',
      'comissao', // Nova coluna calculada
      'marginMode',
      'ctime',
      'utime',
      'positionId'
    ];
    
    const allKeys = Array.from(keys);
    const orderedKeys = [];
    
    // Excluir campos desnecessários ou confusos
    const excludedFields = ['netProfit', 'marginCoin', 'closeFee', 'openFee', 'totalFunding'];
    
    // Adiciona as chaves na ordem de prioridade
    priorityOrder.forEach(key => {
      if (key === 'comissao' || (allKeys.includes(key) && !excludedFields.includes(key))) {
        orderedKeys.push(key);
      }
    });
    
    // Adiciona as chaves restantes que não estão na lista de prioridade (excluindo campos desnecessários)
    allKeys.forEach(key => {
      if (!priorityOrder.includes(key) && !excludedFields.includes(key)) {
        orderedKeys.push(key);
      }
    });
    
    return orderedKeys;
  };

  // Função para calcular a comissão (PNL x 35% apenas para operações positivas)
  const calculateCommission = (pnl) => {
    if (!pnl || isNaN(parseFloat(pnl))) return 0;
    const pnlValue = parseFloat(pnl);
    // Só cobra comissão se o PNL for positivo (lucro)
    return pnlValue > 0 ? pnlValue * 0.35 : 0;
  };

  // Função para calcular o total de comissões
  const calculateTotalCommissions = useCallback((positionsData) => {
    const total = positionsData.reduce((sum, position) => {
      // Inline calculation to avoid dependency issues
      const pnl = parseFloat(position.pnl) || 0;
      const commission = pnl > 0 ? pnl * 0.35 : 0;
      return sum + commission;
    }, 0);
    setTotalCommissions(total);
  }, []);

  // Função para calcular o total de lucro/prejuízo
  const calculateTotalPnL = (positionsData) => {
    return positionsData.reduce((sum, position) => {
      const pnl = parseFloat(position.pnl) || 0;
      return sum + pnl;
    }, 0);
  };

  // Remover filtro local - agora o filtro é aplicado no backend
  // Os dados já vêm filtrados da API conforme as datas selecionadas

  // Função para limpar filtros
  const clearFilters = () => {
    setStartDate('');
    setEndDate('');
    // Os dados serão recarregados automaticamente pelo useEffect do loadFinishedPositions
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={false}
      PaperProps={{
        sx: {
          width: '90vw',
          maxHeight: '90vh',
          margin: '20px'
        }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Operações Finalizadas</Typography>
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

      <DialogContent sx={{ p: 2, overflowX: 'hidden' }}>
        {/* Filtros de Data e Resumo de Comissões */}
        <Card sx={{ mb: 2 }}>
          <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Grid container spacing={1.5}>
               {/* Primeira linha - Filtros de Data */}
               <Grid item xs={12} md={4}>
                 <TextField
                   label="Data Inicial"
                   type="date"
                   value={startDate}
                   onChange={(e) => setStartDate(e.target.value)}
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
                   value={endDate}
                   onChange={(e) => setEndDate(e.target.value)}
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
               
               {/* Segunda linha - Resumos */}
               <Grid item xs={12} md={6}>
                 <Box
                   sx={{
                     p: 0.75,
                     backgroundColor: '#f5f5f5',
                     borderRadius: 1,
                     textAlign: 'center',
                     minHeight: '60px',
                     display: 'flex',
                     flexDirection: 'column',
                     justifyContent: 'center'
                   }}
                 >
                   <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.7rem' }}>
                     Lucro/Prejuízo
                   </Typography>
                   <Typography
                     variant="body2"
                     sx={{
                       color: calculateTotalPnL(filteredPositions) >= 0 ? '#4caf50' : '#f44336',
                       fontWeight: 'bold',
                       fontSize: '0.85rem'
                     }}
                   >
                     {formatValue(calculateTotalPnL(filteredPositions))}
                   </Typography>
                 </Box>
               </Grid>
               <Grid item xs={12} md={6}>
                 <Box
                   sx={{
                     p: 0.75,
                     backgroundColor: '#f5f5f5',
                     borderRadius: 1,
                     textAlign: 'center',
                     minHeight: '60px',
                     display: 'flex',
                     flexDirection: 'column',
                     justifyContent: 'center'
                   }}
                 >
                   <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.7rem' }}>
                     Comissões Pagas
                   </Typography>
                   <Typography
                     variant="body2"
                     sx={{
                       color: totalCommissions > 0 ? '#4caf50' : '#666',
                       fontWeight: 'bold',
                       fontSize: '0.85rem'
                     }}
                   >
                     {formatValue(totalCommissions)}
                   </Typography>
                 </Box>
               </Grid>
             </Grid>
          </CardContent>
        </Card>

        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
        ) : filteredPositions.length === 0 ? (
          <Alert severity="info">Nenhuma operação finalizada encontrada</Alert>
        ) : (
          <>
            <TableContainer 
              component={Paper} 
              sx={{ 
                mb: 2,
                width: '100%',
                overflowX: 'auto',
                '& .MuiTable-root': {
                  minWidth: '100%',
                  borderCollapse: 'separate',
                  borderSpacing: '0'
                }
              }}
            >
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {getAllKeys(filteredPositions).map((key) => (
                      <TableCell 
                        key={key}
                        sx={{
                          whiteSpace: 'nowrap',
                          backgroundColor: 'background.paper',
                          fontWeight: 'bold',
                          textAlign: 'center'
                        }}
                      >
                        {getColumnTitle(key)}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredPositions.map((position, index) => (
                    <TableRow key={index}>
                      {getAllKeys(filteredPositions).map((key) => (
                        <TableCell 
                          key={key}
                          sx={{
                            whiteSpace: 'nowrap',
                            maxWidth: '200px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            textAlign: 'center',
                            ...(key === 'comissao' && calculateCommission(position.pnl) > 0 && {
                              color: '#4caf50 !important',
                              fontWeight: 'bold'
                            })
                          }}
                        >
                          {key === 'comissao' ? 
                            formatValue(calculateCommission(position.pnl)) :
                            key === 'symbol' ? 
                              position[key] || '-' :
                            key === 'leverage' ?
                              position[key] ? `${position[key]}x` : '-' :
                            key === 'holdSide' ?
                              <span
                                style={{
                                  color: position[key]?.toLowerCase() === 'long' ? '#4caf50' : '#f44336',
                                  fontWeight: 'bold',
                                  textTransform: 'uppercase'
                                }}
                              >
                                {position[key] || '-'}
                              </span> :
                            key === 'pnl' ?
                              <span
                                style={{
                                  color: parseFloat(position[key] || 0) >= 0 ? '#4caf50' : '#f44336',
                                  fontWeight: 'bold'
                                }}
                              >
                                {formatValue(position[key])}
                              </span> :
                            key.toLowerCase().includes('time') || key === 'ctime' || key === 'utime' ? 
                              formatDateTime(position[key]) :
                              ['openAvgPrice', 'closeAvgPrice', 'openTotalPos', 'closeTotalPos', 'netProfit'].includes(key) ?
                                formatValue(position[key]) :
                                translateValue(key, position[key]?.toString() || '-')
                          }
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default FinishedOperationsModal;