import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Container, Typography, Card, CardContent, Grid,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Tooltip, Button, CircularProgress, AppBar, Toolbar,
  Alert, Chip
} from '@mui/material';
import { ArrowBack, RefreshRounded, TrendingUp, TrendingDown } from '@mui/icons-material';
import { toast } from 'react-toastify';
import API_CONFIG from '../../config/api';

const UserDashboardView = () => {
    const { userId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [userData, setUserData] = useState(null);
    const [closingTradeId, setClosingTradeId] = useState(null);
    const [error, setError] = useState(null);

    const loadUserData = async (isManualRefresh = false) => {
        if (!isManualRefresh && isRefreshing) return;

        setIsRefreshing(true);
        setError(null);
        
        try {
            console.log(`[DEBUG] Carregando dados do usuário ${userId}`);
            
            const response = await fetch(`${API_CONFIG.baseURL}/api/admin/user/${userId}/dashboard`, {
                method: 'GET',
                credentials: 'include',
                headers: { 
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                },
            });
            
            console.log(`[DEBUG] Response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('[DEBUG] Dados recebidos:', data);
            
            setUserData(data);
            
            if (isManualRefresh) {
                toast.success('Dados atualizados com sucesso!');
            }
            
        } catch (error) {
            console.error('Erro ao carregar dados do usuário:', error);
            setError(error.message);
            
            if (!userData) {
                toast.error('Não foi possível carregar os dados do usuário.');
            } else {
                toast.error('Erro ao atualizar dados.');
            }
        } finally {
            setLoading(false);
            setIsRefreshing(false);
        }
    };

    useEffect(() => {
        if (userId) {
            loadUserData();
            // Atualizar a cada 30 segundos
            const interval = setInterval(() => loadUserData(false), 30000);
            return () => clearInterval(interval);
        }
    }, [userId]);
    
    const handleCloseTrade = async (tradeId) => {
        if (closingTradeId) return;
        
        setClosingTradeId(tradeId);
        try {
            const response = await fetch(`${API_CONFIG.baseURL}/api/admin/trades/${tradeId}/close`, {
                method: 'POST',
                credentials: 'include',
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erro ao fechar a operação.');
            }
            
            toast.success('Ordem de fechamento enviada com sucesso!');
            await loadUserData();
            
        } catch (error) {
            console.error('Erro ao fechar trade:', error);
            toast.error(`Falha ao fechar a operação: ${error.message}`);
        } finally {
            setClosingTradeId(null);
        }
    };

    const formatUsd = (value, maxFractionDigits = 2) => {
        const numValue = parseFloat(value) || 0;
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: maxFractionDigits,
        }).format(numValue);
    };

    const formatNumber = (value, maxFractionDigits = 4) => {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return 'N/A';
        
        return new Intl.NumberFormat('pt-BR', {
            style: 'decimal',
            minimumFractionDigits: 2,
            maximumFractionDigits: maxFractionDigits,
        }).format(numValue);
    };
    
    const formatPercentage = (value) => {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return 'N/A';
        
        return `${numValue.toFixed(2)}%`;
    };
    
    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        
        try {
            // Se for timestamp em milissegundos
            const timestamp = parseInt(dateString);
            if (!isNaN(timestamp)) {
                return new Date(timestamp).toLocaleString('pt-BR');
            }
            
            // Se for string de data
            return new Date(dateString).toLocaleString('pt-BR');
        } catch {
            return 'N/A';
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', bgcolor: '#121212' }}>
                <CircularProgress size={60} sx={{ color: '#f0b90b' }} />
            </Box>
        );
    }
    
    if (error && !userData) {
        return (
            <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', bgcolor: '#121212', p: 3 }}>
                <Alert severity="error" sx={{ mb: 2, maxWidth: 500 }}>
                    {error}
                </Alert>
                <Button variant="contained" onClick={() => navigate('/admin')} sx={{ bgcolor: '#f0b90b', '&:hover': { bgcolor: '#d4a00a' } }}>
                    Voltar ao Dashboard Admin
                </Button>
            </Box>
        );
    }

    if (!userData) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', bgcolor: '#121212' }}>
                <Typography color="white">Nenhum dado encontrado</Typography>
            </Box>
        );
    }

    const { user, stats, balance, trades, positions } = userData;
    const openPositions = positions || [];
    const closedTrades = trades || [];
    const userBalance = balance || {};
    const userStats = stats || {};

    return (
        <Box sx={{ display: 'flex', bgcolor: '#121212', minHeight: '100vh' }}>
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: '#1a1a1a' }}>
                <Toolbar>
                    <IconButton edge="start" color="inherit" onClick={() => navigate('/admin')} sx={{ mr: 2 }}>
                        <ArrowBack />
                    </IconButton>
                    <Typography variant="subtitle1" noWrap component="div" sx={{ flexGrow: 1, fontSize: '1.25rem', fontWeight: 600 }}>
                        Dashboard - {user?.full_name || 'Usuário'}
                    </Typography>
                    <Chip 
                        label={user?.api_configured ? 'API Configurada' : 'API Não Configurada'} 
                        color={user?.api_configured ? 'success' : 'warning'}
                        size="small"
                        sx={{ mr: 2 }}
                    />
                    <Tooltip title="Atualizar Dados">
                        <span>
                            <IconButton onClick={() => loadUserData(true)} color="inherit" disabled={isRefreshing}>
                                {isRefreshing ? <CircularProgress size={24} color="inherit" /> : <RefreshRounded />}
                            </IconButton>
                        </span>
                    </Tooltip>
                </Toolbar>
            </AppBar>
            
            <Box component="main" sx={{ flexGrow: 1, p: 3, mt: '64px' }}>
                <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
                    
                    {/* Cards de Estatísticas */}
                    <Grid container spacing={3} sx={{ mb: 4 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Card sx={{ bgcolor: '#1e1e1e', border: '1px solid #333' }}>
                                <CardContent>
                                    <Typography color="#888" gutterBottom variant="body2">
                                        Saldo Total
                                    </Typography>
                                    <Typography variant="h5" sx={{ color: '#2196f3', fontWeight: 'bold' }}>
                                        {formatUsd(userBalance.total_balance)}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                            <Card sx={{ bgcolor: '#1e1e1e', border: '1px solid #333' }}>
                                <CardContent>
                                    <Typography color="#888" gutterBottom variant="body2">
                                        PnL Não Realizado
                                    </Typography>
                                    <Typography 
                                        variant="h5" 
                                        sx={{ 
                                            color: (userBalance.unrealized_pnl || 0) >= 0 ? '#4caf50' : '#f44336',
                                            fontWeight: 'bold'
                                        }}
                                    >
                                        {formatUsd(userBalance.unrealized_pnl)}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                            <Card sx={{ bgcolor: '#1e1e1e', border: '1px solid #333' }}>
                                <CardContent>
                                    <Typography color="#888" gutterBottom variant="body2">
                                        Total de Trades
                                    </Typography>
                                    <Typography variant="h5" sx={{ color: '#ff9800', fontWeight: 'bold' }}>
                                        {userStats.total_trades || 0}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                            <Card sx={{ bgcolor: '#1e1e1e', border: '1px solid #333' }}>
                                <CardContent>
                                    <Typography color="#888" gutterBottom variant="body2">
                                        Taxa de Vitória
                                    </Typography>
                                    <Typography variant="h5" sx={{ color: '#9c27b0', fontWeight: 'bold' }}>
                                        {formatPercentage(userStats.win_rate)}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    {/* Posições Abertas */}
                    <Card sx={{ bgcolor: '#1e1e1e', border: '1px solid #333', mb: 3 }}>
                        <CardContent>
                            <Typography variant="h6" sx={{ color: '#f0b90b', mb: 2, display: 'flex', alignItems: 'center' }}>
                                <TrendingUp sx={{ mr: 1 }} />
                                Posições Abertas ({openPositions.length})
                            </Typography>
                            
                            {openPositions.length > 0 ? (
                                <TableContainer>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Símbolo</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Lado</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Tamanho</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Preço de Entrada</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>PnL ($)</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>ROE (%)</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Alavancagem</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Ações</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {openPositions.map((position, index) => (
                                                <TableRow key={position.id || index}>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {position.symbol || 'N/A'}
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip 
                                                            label={position.side || 'N/A'}
                                                            color={position.side?.toLowerCase() === 'long' ? 'success' : 'error'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {formatNumber(position.size)}
                                                    </TableCell>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {formatUsd(position.entry_price, 4)}
                                                    </TableCell>
                                                    <TableCell sx={{ 
                                                        color: (position.pnl || position.unrealized_pnl || 0) >= 0 ? '#4caf50' : '#f44336',
                                                        fontWeight: 'bold'
                                                    }}>
                                                        {formatUsd(position.pnl || position.unrealized_pnl)}
                                                    </TableCell>
                                                    <TableCell sx={{ 
                                                        color: (position.roe_percentage || 0) >= 0 ? '#4caf50' : '#f44336',
                                                        fontWeight: 'bold'
                                                    }}>
                                                        {formatPercentage(position.roe_percentage)}
                                                    </TableCell>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {position.leverage || 'N/A'}x
                                                    </TableCell>
                                                    <TableCell>
                                                        <Button
                                                            variant="contained"
                                                            color="error"
                                                            size="small"
                                                            onClick={() => handleCloseTrade(position.id)}
                                                            disabled={closingTradeId === position.id}
                                                            sx={{ minWidth: '80px' }}
                                                        >
                                                            {closingTradeId === position.id ? (
                                                                <CircularProgress size={16} color="inherit" />
                                                            ) : (
                                                                'Fechar'
                                                            )}
                                                        </Button>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            ) : (
                                <Box sx={{ textAlign: 'center', py: 4 }}>
                                    <Typography color="#888">
                                        Nenhuma posição aberta no momento.
                                    </Typography>
                                </Box>
                            )}
                        </CardContent>
                    </Card>

                    {/* Histórico de Trades */}
                    <Card sx={{ bgcolor: '#1e1e1e', border: '1px solid #333' }}>
                        <CardContent>
                            <Typography variant="h6" sx={{ color: '#f0b90b', mb: 2, display: 'flex', alignItems: 'center' }}>
                                <TrendingDown sx={{ mr: 1 }} />
                                Histórico de Trades Recentes
                            </Typography>
                            
                            {closedTrades.length > 0 ? (
                                <TableContainer>
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Símbolo</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Lado</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Tamanho</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Preço</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>PnL ($)</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Status</TableCell>
                                                <TableCell sx={{ color: '#f0b90b', fontWeight: 'bold' }}>Data</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {closedTrades.slice(0, 10).map((trade, index) => (
                                                <TableRow key={trade.id || index}>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {trade.symbol || 'N/A'}
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip 
                                                            label={trade.side || 'N/A'}
                                                            color={trade.side?.toLowerCase() === 'buy' ? 'success' : 'error'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {formatNumber(trade.size)}
                                                    </TableCell>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {formatUsd(trade.price, 4)}
                                                    </TableCell>
                                                    <TableCell sx={{ 
                                                        color: (trade.pnl || 0) >= 0 ? '#4caf50' : '#f44336',
                                                        fontWeight: 'bold'
                                                    }}>
                                                        {formatUsd(trade.pnl)}
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip 
                                                            label={trade.status || 'N/A'}
                                                            color={trade.status === 'filled' ? 'success' : 'default'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                    <TableCell sx={{ color: 'white' }}>
                                                        {formatDate(trade.closed_at || trade.updated_at || trade.created_at)}
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            ) : (
                                <Box sx={{ textAlign: 'center', py: 4 }}>
                                    <Typography color="#888">
                                        Nenhum trade encontrado.
                                    </Typography>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Container>
            </Box>
        </Box>
    );
};

export default UserDashboardView;