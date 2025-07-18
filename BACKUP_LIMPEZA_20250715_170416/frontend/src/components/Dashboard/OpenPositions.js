import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  useTheme,
  Dialog,
  DialogContent,
  Alert,
  Button,
  Skeleton
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  Schedule,
  Close,
  Share,
  Download,
  Warning,
  Lock
} from '@mui/icons-material';
import pnlBackground from '../../assets/pnl-background.png';
import dashboardService from '../../services/dashboardService';

const OpenPositions = ({ user, hideValues = false }) => {
  const theme = useTheme();
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [closingPosition, setClosingPosition] = useState(null);
  const [debugInfo, setDebugInfo] = useState('');

  const calculateROE = (position) => {
    if (!position) {
      return 0;
    }
    
    // Usar ROE diretamente da API se disponível (já calculado com margem real)
    if (position.roe !== undefined && position.roe !== null) {
      return parseFloat(position.roe);
    }
    
    // Fallback: calcular usando PnL e margem real se disponível
    const unrealizedPnl = parseFloat(position.unrealized_pnl || 0);
    const margin = parseFloat(position.margin || 0);
    
    if (margin === 0) return 0;
    
    const roe = (unrealizedPnl / margin) * 100;
    return roe;
  };

  const loadPositions = async (showLoading = false) => {
    if (refreshing) return;
    
    try {
      setError('');
      if (showLoading) {
        setLoading(true);
      }
      console.log('OpenPositions - Carregando posições...');
      
      const response = await dashboardService.getOpenPositions();
      console.log('OpenPositions - Resposta recebida:', response);
      
      if (response && response.success) {
        const positionsData = response.data || [];
        console.log('OpenPositions - Posições encontradas:', positionsData);
        setPositions(positionsData);
        setDebugInfo(`${positionsData.length} posições carregadas`);
      } else {
        const errorMsg = response?.message || 'Erro desconhecido ao carregar posições';
        console.log('OpenPositions - Erro na resposta:', errorMsg);
        setError(errorMsg);
        setDebugInfo(`Erro: ${errorMsg}`);
      }
    } catch (error) {
      console.error('OpenPositions - Erro ao carregar posições:', error);
      
      // Verificar se é erro de autenticação
      if (error.message === 'Login necessário' || error.status === 401) {
        setError('Sessão expirada. Você será redirecionado para o login.');
        setDebugInfo('Erro de autenticação');
        // O interceptador já vai lidar com o redirecionamento
      } else {
        const errorMsg = error.message || 'Erro ao conectar com o servidor';
        setError(errorMsg);
        setDebugInfo(`Erro de conexão: ${errorMsg}`);
      }
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

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

  useEffect(() => {
    loadPositions(true); // Primeira carga com loading
    
    // Timer para atualização automática a cada 30 segundos
    const interval = setInterval(() => {
      loadPositions(false); // Atualizações automáticas sem loading
    }, 30000); // 30 segundos
    
    // Cleanup do timer quando o componente for desmontado
    return () => clearInterval(interval);
  }, []);

  const handleClosePosition = async (position) => {
    try {
      setClosingPosition(position.symbol);
      const response = await dashboardService.closePosition(position.symbol, position.side);
      
      if (response.success) {
        // Recarregar posições após fechar
        await loadPositions();
        setError('');
      } else {
        setError(response.message || 'Erro ao encerrar posição');
      }
    } catch (error) {
      console.error('Erro ao encerrar posição:', error);
      setError(error.message || 'Erro ao encerrar posição');
    } finally {
      setClosingPosition(null);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPositions();
    setRefreshing(false);
  };

  const handleShare = (position) => {
    setSelectedPosition(position);
    setShareModalOpen(true);
  };

  const handleCloseShareModal = () => {
    setShareModalOpen(false);
    setSelectedPosition(null);
  };

  const downloadCard = async () => {
    const element = document.getElementById('share-card');
    if (element) {
      try {
        // Importar dinamicamente para evitar warnings
        const html2canvas = await import('html2canvas');
        const canvas = await html2canvas.default(element, {
          backgroundColor: null,
          scale: 2,
          useCORS: true,
          allowTaint: true
        });
        
        const link = document.createElement('a');
        link.download = `nautilus-trade-${selectedPosition?.symbol || 'position'}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
      } catch (error) {
        console.error('Erro ao gerar imagem:', error);
      }
    }
  };

  const formatCurrency = (value, currency = 'USDT') => {
    if (hideValues) return `*** ${currency}`;
    const numValue = parseFloat(value || 0);
    
    // Para valores muito pequenos, mostrar até 8 casas decimais
    if (Math.abs(numValue) < 0.001 && numValue !== 0) {
      return `${numValue.toFixed(8)} ${currency}`;
    }
    
    // Para valores pequenos, mostrar até 6 casas decimais
    if (Math.abs(numValue) < 0.1 && numValue !== 0) {
      return `${numValue.toFixed(6)} ${currency}`;
    }
    
    // Para valores menores que 1, mostrar até 4 casas decimais
    if (Math.abs(numValue) < 1) {
      return `${numValue.toFixed(4)} ${currency}`;
    }
    
    // Para valores maiores, mostrar 2 casas decimais
    return `${numValue.toFixed(2)} ${currency}`;
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return '0%';
    
    // Para percentuais muito pequenos, mostrar mais casas decimais
    if (Math.abs(value) < 0.01 && value !== 0) {
      return `${value >= 0 ? '+' : ''}${parseFloat(value).toFixed(6)}%`;
    }
    
    // Para percentuais pequenos, mostrar 4 casas decimais
    if (Math.abs(value) < 1) {
      return `${value >= 0 ? '+' : ''}${parseFloat(value).toFixed(4)}%`;
    }
    
    // Para percentuais maiores, mostrar 2 casas decimais
    return `${value >= 0 ? '+' : ''}${parseFloat(value).toFixed(2)}%`;
  };

  const getColorByValue = (value) => {
    if (value > 0) return '#02c076'; // Verde
    if (value < 0) return '#f84960'; // Vermelho
    return '#848e9c'; // Cinza neutro
  };

  const getSideColor = (side) => {
    return side === 'long' ? '#02c076' : '#f84960';
  };

  const getSideIcon = (side) => {
    return side === 'long' ? <TrendingUp /> : <TrendingDown />;
  };

  // Componente ShareCard
  const ShareCard = ({ position }) => {
    if (!position) return null;

    const roe = calculateROE(position);
    const currentDate = new Date().toLocaleString('pt-BR', {
      timeZone: 'America/Sao_Paulo',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });

    // Extrair informações do usuário
    const userName = user?.full_name?.trim() || user?.email?.split('@')[0] || 'Usuário';
    const userInitial = userName.charAt(0).toUpperCase();

    return (
      <Box
        id="share-card"
        sx={{
          width: 400,
          height: 600,
          backgroundImage: `url(${pnlBackground})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          position: 'relative',
          borderRadius: 3,
          overflow: 'hidden',
          color: 'white',
          fontFamily: 'Arial, sans-serif',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            borderRadius: 'inherit',
            zIndex: 1
          }
        }}
      >
        {/* User info */}
        <Box sx={{ px: 3, py: 2, mt: 12, display: 'flex', alignItems: 'center', gap: 2, position: 'relative', zIndex: 2 }}>
          <Box
            sx={{
              width: 50,
              height: 50,
              borderRadius: '50%',
              background: 'linear-gradient(45deg, #00bcd4, #0097a7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 20,
              fontWeight: 'bold'
            }}
          >
            {userInitial}
          </Box>
          <Box>
            <Typography sx={{ fontSize: 18, fontWeight: 'bold' }}>{userName}</Typography>
          </Box>
        </Box>

        {/* Trade info */}
        <Box sx={{ px: 3, py: 2, position: 'relative', zIndex: 2 }}>
          <Typography sx={{ fontSize: 32, fontWeight: 'bold', mb: 1 }}>
            {position.symbol}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Typography 
              sx={{ 
                fontSize: 16, 
                color: position.side === 'long' ? '#02c076' : '#f84960',
                fontWeight: 'bold'
              }}
            >
              {position.side === 'long' ? 'Compra' : 'Venda'}
            </Typography>
            <Typography sx={{ fontSize: 16, color: '#b0bec5' }}>|</Typography>
            <Typography sx={{ fontSize: 16, fontWeight: 'bold' }}>
              {position.leverage}x
            </Typography>
          </Box>

          <Typography 
            sx={{ 
              fontSize: 48, 
              fontWeight: 'bold', 
              color: roe >= 0 ? '#02c076' : '#f84960',
              mb: 3,
              textAlign: 'center'
            }}
          >
            {formatPercentage(roe)}
          </Typography>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography sx={{ fontSize: 14, color: '#78909c' }}>Preço de entrada</Typography>
            <Typography sx={{ fontSize: 16, fontWeight: 'bold', textAlign: 'right' }}>
              {(() => {
                const price = parseFloat(position.entry_price || 0);
                if (Math.abs(price) < 0.01 && price !== 0) {
                  return `$${price.toFixed(8)}`;
                }
                if (Math.abs(price) < 1) {
                  return `$${price.toFixed(6)}`;
                }
                if (Math.abs(price) < 100) {
                  return `$${price.toFixed(4)}`;
                }
                return `$${price.toFixed(3)}`;
              })()} 
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography sx={{ fontSize: 14, color: '#78909c' }}>Preço atual (referência)</Typography>
            <Typography sx={{ fontSize: 16, fontWeight: 'bold', textAlign: 'right' }}>
              {(() => {
                const price = parseFloat(position.mark_price || 0);
                if (Math.abs(price) < 0.01 && price !== 0) {
                  return `$${price.toFixed(8)}`;
                }
                if (Math.abs(price) < 1) {
                  return `$${price.toFixed(6)}`;
                }
                if (Math.abs(price) < 100) {
                  return `$${price.toFixed(4)}`;
                }
                return `$${price.toFixed(3)}`;
              })()} 
            </Typography>
          </Box>

          {/* Share info - moved to bottom center */}
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography sx={{ fontSize: 12, color: '#78909c' }}>
              Compartilhado em: {currentDate} (UTC-3)
            </Typography>
          </Box>
        </Box>
      </Box>
    );
  };

  // Loading state
  if (loading) {
    return (
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, fontSize: '1.1rem' }}>
          <TrendingUp color="primary" sx={{ fontSize: 20 }} />
          Posições Abertas
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="rectangular" height={40} />
          <Skeleton variant="rectangular" height={40} />
          <Skeleton variant="rectangular" height={40} />
        </Box>
      </Paper>
    );
  }

  // Error state
  if (error) {
    return (
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '1.1rem' }}>
            <TrendingUp color="primary" sx={{ fontSize: 20 }} />
            📊 Posições Abertas
          </Typography>
          
          <IconButton onClick={handleRefresh} disabled={refreshing} size="small">
            <Refresh />
          </IconButton>
        </Box>

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 280,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`,
            p: 2
          }}
        >
          {error.includes('API não configurada') ? (
            <>
              <Lock sx={{ fontSize: 40, color: 'text.secondary', mb: 1.5 }} />
              <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ fontSize: '1rem' }}>
                API Bitget não configurada
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ fontSize: '0.85rem' }}>
                Configure suas credenciais da API Bitget para visualizar posições abertas.
              </Typography>
            </>
          ) : (
            <>
              <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1.5 }} />
              <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ fontSize: '1rem' }}>
                Erro ao carregar posições
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ fontSize: '0.85rem', mb: 2 }}>
                {error}
              </Typography>
              <Alert severity="error" sx={{ width: '100%', fontSize: '0.8rem' }}>
                Verifique sua conexão e tente novamente.
              </Alert>
            </>
          )}
        </Box>
      </Paper>
    );
  }

  // No positions state
  if (!positions || positions.length === 0) {
    return (
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '1.1rem' }}>
            <TrendingUp color="primary" sx={{ fontSize: 20 }} />
            📊 Posições Abertas
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Timer Visual */}
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress
                variant="determinate"
                value={progress}
                size={24}
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
                <Schedule sx={{ fontSize: 12, color: 'text.secondary' }} />
              </Box>
            </Box>
            
            <IconButton onClick={handleRefresh} disabled={refreshing} size="small">
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 280,
            bgcolor: 'background.default',
            borderRadius: 1,
            border: `1px dashed ${theme.palette.divider}`,
            p: 2
          }}
        >
          <TrendingUp sx={{ fontSize: 40, color: 'text.secondary', mb: 1.5 }} />
          <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ fontSize: '1rem' }}>
            Nenhuma posição aberta
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ fontSize: '0.85rem' }}>
            Você não possui posições abertas no momento. As posições aparecerão aqui quando você abrir operações na Bitget.
          </Typography>
        </Box>

        {/* Debug Info */}
        {process.env.NODE_ENV === 'development' && debugInfo && (
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem', mt: 1, display: 'block' }}>
            Resumo: {debugInfo}
          </Typography>
        )}
      </Paper>
    );
  }

  // Main positions display when there are positions
  return (
    <>
      <Paper sx={{ p: 2.5, height: 380 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '1.1rem' }}>
            <TrendingUp color="primary" sx={{ fontSize: 20 }} />
            📊 Posições Abertas ({positions.length})
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Timer Visual */}
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress
                variant="determinate"
                value={progress}
                size={24}
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
                <Schedule sx={{ fontSize: 12, color: 'text.secondary' }} />
              </Box>
            </Box>
            
            <IconButton onClick={handleRefresh} disabled={refreshing} size="small">
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        <TableContainer sx={{ maxHeight: 300 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', paddingLeft: '69px' }}>Ativo</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>Lado</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>Tamanho</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>Preço Entrada</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>Preço Atual</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>Margem (USDT)</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>PnL (USDT)</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>ROE</TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center' }}>Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {positions.map((position, index) => {
                const roe = calculateROE(position);
                return (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: '45px', textAlign: 'left', mr: 1 }}>
                          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                            {position.leverage}x
                          </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {position.symbol}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Chip
                        icon={getSideIcon(position.side)}
                        label={position.side.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: `${getSideColor(position.side)}20`,
                          color: getSideColor(position.side),
                          fontSize: '0.7rem',
                          fontWeight: 'bold'
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.8rem', textAlign: 'center' }}>
                      {hideValues ? '***' : parseFloat(position.size || 0).toFixed(4)}
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.8rem', textAlign: 'center' }}>
                      {formatCurrency(position.entry_price, '')}
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.8rem', textAlign: 'center' }}>
                      {formatCurrency(position.mark_price, '')}
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.8rem', textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#66FFCC' }}>
                        {hideValues ? '***' : formatCurrency(position.margin || position.margin_size || 0, '')}
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: getColorByValue(position.unrealized_pnl || 0), fontWeight: 'bold' }}>
                        {hideValues ? '***' : formatCurrency(position.unrealized_pnl || 0)}
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: getColorByValue(roe), fontWeight: 'bold' }}>
                        {formatPercentage(roe)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5 }}>
                        <Tooltip title="Compartilhar">
                          <IconButton
                            size="small"
                            onClick={() => handleShare(position)}
                            color="primary"
                          >
                            <Share sx={{ fontSize: 16 }} />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Fechar Posição">
                          <span>
                            <IconButton
                              size="small"
                              onClick={() => handleClosePosition(position)}
                              disabled={closingPosition === position.symbol}
                              color="error"
                            >
                              {closingPosition === position.symbol ? (
                                <CircularProgress size={16} />
                              ) : (
                                <Close sx={{ fontSize: 16 }} />
                              )}
                            </IconButton>
                          </span>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Debug Info */}
        {process.env.NODE_ENV === 'development' && debugInfo && (
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem', mt: 1, display: 'block' }}>
            Resumo: {debugInfo}
          </Typography>
        )}
      </Paper>

      {/* Modal de Compartilhamento */}
      <Dialog 
        open={shareModalOpen} 
        onClose={handleCloseShareModal}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { 
            maxHeight: '90vh',
            height: 'auto'
          }
        }}
      >
        <DialogContent sx={{ 
          p: 3, 
          backgroundColor: '#f5f5f5',
          maxHeight: '80vh',
          overflowY: 'auto',
          overflowX: 'hidden'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Compartilhar Operação</Typography>
            <IconButton onClick={handleCloseShareModal} size="small">
              <Close />
            </IconButton>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <ShareCard position={selectedPosition} />
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button 
              variant="contained" 
              startIcon={<Download />}
              onClick={downloadCard}
              sx={{ 
                backgroundColor: '#00bcd4',
                '&:hover': {
                  backgroundColor: '#0097a7'
                }
              }}
            >
              Baixar Imagem
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default OpenPositions;