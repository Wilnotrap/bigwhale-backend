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
  Lock,
  SmartToy,
  Person
} from '@mui/icons-material';
import Lottie from 'react-lottie';
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

  // Configuração da animação Lottie para o alvo (🎯)
  const targetAnimationOptions = {
    loop: true,
    autoplay: true,
    animationData: null,
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice'
    },
    path: 'https://assets5.lottiefiles.com/packages/lf20_h9SJbwh6ky.json' // Animação de sucesso/alvo
  };

  // Componente para exibir indicadores de takes
  const TakesIndicator = ({ takesHit }) => {
    if (!takesHit || takesHit === 0) {
      return null;
    }

    const targets = [];
    for (let i = 0; i < takesHit; i++) {
      targets.push(
        <Tooltip key={i} title={`Take ${i + 1} atingido!`} arrow>
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 28,
              height: 28,
              mx: 0.5,
              borderRadius: '50%',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              border: '2px solid #4CAF50',
              transition: 'all 0.3s ease',
              cursor: 'help',
              animation: 'pulse-success 2s infinite',
              '&:hover': {
                transform: 'scale(1.1)',
                boxShadow: '0 4px 12px rgba(76, 175, 80, 0.4)'
              }
            }}
          >
            <Lottie
              options={targetAnimationOptions}
              height={20}
              width={20}
              style={{ pointerEvents: 'none' }}
            />
          </Box>
        </Tooltip>
      );
    }

    // Ícone de escudo para operações protegidas (2+ takes)
    const shieldIcon = takesHit >= 2 ? (
      <Tooltip title="Operação protegida!" arrow>
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 32,
            height: 32,
            mx: 0.5,
            borderRadius: '50%',
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            border: '2px solid #2196F3',
            transition: 'all 0.3s ease',
            cursor: 'help',
            animation: 'pulse-success 3s infinite',
            '&:hover': {
              transform: 'scale(1.1)',
              boxShadow: '0 4px 12px rgba(33, 150, 243, 0.4)'
            }
          }}
        >
          🛡️
        </Box>
      </Tooltip>
    ) : null;

    return (
      <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
        {targets}
        {shieldIcon}
        <Typography
          variant="caption"
          sx={{
            ml: 1,
            color: '#4CAF50',
            fontWeight: 'bold',
            fontSize: '0.75rem'
          }}
        >
          {takesHit} Take{takesHit > 1 ? 's' : ''}
        </Typography>
      </Box>
    );
  };

  // Função para detectar origem da operação baseada no ID
  const detectOperationOrigin = (position) => {
    // Operações com ID = Nautilus automatizado
    // Operações sem ID = Manual do usuário
    const hasId = position.id && position.id !== null && position.id !== undefined && position.id !== '';

    return {
      isNautilus: hasId,
      isManual: !hasId,
      icon: hasId ? SmartToy : Person,
      tooltip: hasId ? 'Operação Automatizada (Nautilus)' : 'Operação Manual (Usuário)',
      color: hasId ? '#00bcd4' : '#757575',
      bgColor: hasId ? 'rgba(0, 188, 212, 0.1)' : 'rgba(117, 117, 117, 0.1)'
    };
  };

  // Configurações das animações Lottie online
  const robotLottieOptions = {
    loop: true,
    autoplay: true,
    animationData: null,
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice'
    },
    path: 'https://assets9.lottiefiles.com/packages/lf20_x62chJ.json' // Animação de robô/automação
  };

  // Componente de ícone animado simples e funcional
  const SuperAnimatedOriginIcon = ({ origin }) => {
    const [isHovered, setIsHovered] = useState(false);
    
    return (
      <Tooltip
        title={origin.isNautilus ? "Operação Automática (Nautilus)" : "Operação Aberta pelo Usuário"}
        arrow
        placement="top"
        enterDelay={300}
        leaveDelay={100}
      >
        <Box
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 36,
            height: 36,
            borderRadius: '50%',
            backgroundColor: origin.bgColor,
            border: `3px solid ${origin.color}`,
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            cursor: 'help',
            position: 'relative',
            overflow: 'visible',
            animation: origin.isNautilus ? 'nautilus-container-glow 3s infinite' : 'user-container-pulse 4s infinite',
            '&:hover': {
              transform: 'scale(1.3)',
              boxShadow: `0 8px 25px ${origin.color}80`,
              borderWidth: '4px',
              '&::before': {
                opacity: 1,
                transform: 'scale(1.5)'
              }
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: '-100%',
              left: '-100%',
              width: '300%',
              height: '300%',
              background: origin.isNautilus
                ? 'conic-gradient(from 0deg, transparent, rgba(0, 188, 212, 0.4), transparent, rgba(38, 198, 218, 0.3), transparent)'
                : 'radial-gradient(circle, rgba(117, 117, 117, 0.3), transparent 70%)',
              animation: origin.isNautilus ? 'background-spin 4s linear infinite' : 'user-ripple-wave 3s ease-out infinite',
              opacity: 0,
              transition: 'all 0.4s ease',
              borderRadius: '50%'
            }
          }}
        >
          {/* Conteúdo principal do ícone */}
          {origin.isNautilus ? (
            // Para Nautilus: Robô girando com efeitos
            <Box sx={{ position: 'relative', zIndex: 2 }}>
              {/* Emoji de robô girando */}
              <Box
                sx={{
                  fontSize: '20px',
                  animation: 'robot-spin-bounce 2s ease-in-out infinite',
                  filter: `drop-shadow(0 0 8px ${origin.color}80)`,
                  position: 'relative',
                  zIndex: 3
                }}
              >
                🤖
              </Box>

              {/* Ícone SmartToy girando por trás */}
              <SmartToy
                sx={{
                  color: origin.color,
                  fontSize: 18,
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  zIndex: 1,
                  animation: 'icon-continuous-spin 3s linear infinite',
                  opacity: 0.6
                }}
              />
            </Box>
          ) : (
            // Para usuário manual: Pessoa girando
            <Box sx={{ position: 'relative', zIndex: 2 }}>
              {/* Emoji de pessoa girando */}
              <Box
                sx={{
                  fontSize: '20px',
                  animation: 'user-spin-wobble 2.5s ease-in-out infinite',
                  filter: isHovered ? `drop-shadow(0 0 8px ${origin.color}60)` : 'none',
                  position: 'relative',
                  zIndex: 3
                }}
              >
                👤
              </Box>

              {/* Ícone Person girando por trás */}
              <Person
                sx={{
                  color: origin.color,
                  fontSize: 18,
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  zIndex: 1,
                  animation: 'icon-reverse-spin 4s linear infinite',
                  opacity: 0.5
                }}
              />
            </Box>
          )}

          {/* Partículas orbitais para Nautilus */}
          {origin.isNautilus && (
            <>
              {[...Array(4)].map((_, i) => (
                <Box
                  key={i}
                  sx={{
                    position: 'absolute',
                    width: 4,
                    height: 4,
                    backgroundColor: i % 2 === 0 ? '#00bcd4' : '#26c6da',
                    borderRadius: '50%',
                    top: '50%',
                    left: '50%',
                    transformOrigin: '0 0',
                    animation: `orbital-motion-${i + 1} ${2 + (i * 0.5)}s linear infinite`,
                    opacity: 0.8,
                    zIndex: 1
                  }}
                />
              ))}

              {/* Anel de energia rotativo */}
              <Box
                sx={{
                  position: 'absolute',
                  width: '140%',
                  height: '140%',
                  border: '2px solid transparent',
                  borderTop: `2px solid ${origin.color}60`,
                  borderRadius: '50%',
                  animation: 'energy-ring-spin 2s linear infinite',
                  top: '-20%',
                  left: '-20%',
                  zIndex: 0
                }}
              />
            </>
          )}

          {/* Ondas pulsantes para usuário manual */}
          {origin.isManual && (
            <>
              {[1, 2].map((wave) => (
                <Box
                  key={wave}
                  sx={{
                    position: 'absolute',
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    border: `2px solid ${origin.color}${40 - (wave * 15)}`,
                    animation: `user-pulse-wave-${wave} ${2 + wave}s ease-out infinite`,
                    animationDelay: `${wave * 0.8}s`,
                    zIndex: 0
                  }}
                />
              ))}
            </>
          )}

          {/* Indicador de status piscante */}
          <Box
            sx={{
              position: 'absolute',
              top: -3,
              right: -3,
              width: 10,
              height: 10,
              backgroundColor: origin.isNautilus ? '#4CAF50' : '#FF9800',
              borderRadius: '50%',
              border: '2px solid white',
              animation: origin.isNautilus ? 'status-blink-green 1.5s infinite' : 'status-blink-orange 2s infinite',
              zIndex: 4,
              boxShadow: `0 0 6px ${origin.isNautilus ? '#4CAF50' : '#FF9800'}80`
            }}
          />
        </Box>
      </Tooltip>
    );
  };

  // Componente de ícone animado aprimorado (versão original mantida como fallback)
  const AnimatedOriginIcon = ({ origin }) => {
    const IconComponent = origin.icon;

    return (
      <Tooltip title={origin.tooltip} arrow>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 32,
            height: 32,
            borderRadius: '50%',
            backgroundColor: origin.bgColor,
            border: `2px solid ${origin.color}`,
            transition: 'all 0.3s ease',
            cursor: 'help',
            position: 'relative',
            overflow: 'hidden',
            animation: origin.isNautilus ? 'nautilus-glow 2.5s infinite' : 'user-pulse 3s infinite',
            '&:hover': {
              transform: 'scale(1.15)',
              boxShadow: `0 6px 20px ${origin.color}60`,
              '&::before': {
                opacity: 1
              }
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: '-50%',
              left: '-50%',
              width: '200%',
              height: '200%',
              background: origin.isNautilus
                ? 'conic-gradient(from 0deg, transparent, rgba(0, 188, 212, 0.3), transparent)'
                : 'radial-gradient(circle, rgba(117, 117, 117, 0.2), transparent)',
              animation: origin.isNautilus ? 'spin-gradient 3s linear infinite' : 'none',
              opacity: 0,
              transition: 'opacity 0.3s ease'
            }
          }}
        >
          <IconComponent
            sx={{
              color: origin.color,
              fontSize: 18,
              zIndex: 1,
              position: 'relative',
              animation: origin.isNautilus
                ? 'robot-dance 2s ease-in-out infinite'
                : 'user-bounce 2.5s ease-in-out infinite',
              filter: origin.isNautilus ? 'drop-shadow(0 0 4px rgba(0, 188, 212, 0.6))' : 'none'
            }}
          />

          {/* Partículas animadas para Nautilus */}
          {origin.isNautilus && (
            <>
              <Box
                sx={{
                  position: 'absolute',
                  width: 4,
                  height: 4,
                  backgroundColor: '#00bcd4',
                  borderRadius: '50%',
                  top: '10%',
                  right: '15%',
                  animation: 'particle-float-1 2s ease-in-out infinite',
                  opacity: 0.7
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  width: 3,
                  height: 3,
                  backgroundColor: '#26c6da',
                  borderRadius: '50%',
                  bottom: '15%',
                  left: '20%',
                  animation: 'particle-float-2 2.5s ease-in-out infinite',
                  opacity: 0.8
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  width: 2,
                  height: 2,
                  backgroundColor: '#4dd0e1',
                  borderRadius: '50%',
                  top: '60%',
                  right: '25%',
                  animation: 'particle-float-3 1.8s ease-in-out infinite',
                  opacity: 0.6
                }}
              />
            </>
          )}

          {/* Efeito de pulso para usuário manual */}
          {origin.isManual && (
            <Box
              sx={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                borderRadius: '50%',
                border: '2px solid rgba(117, 117, 117, 0.3)',
                animation: 'user-ripple 2s ease-out infinite'
              }}
            />
          )}
        </Box>
      </Tooltip>
    );
  };


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
      {/* Adicionar estilos CSS para animações aprimoradas */}
      <style>
        {`
          /* Animações originais */
          @keyframes pulse-glow {
            0% {
              box-shadow: 0 0 5px rgba(0, 188, 212, 0.4);
              transform: scale(1);
            }
            50% {
              box-shadow: 0 0 20px rgba(0, 188, 212, 0.8);
              transform: scale(1.05);
            }
            100% {
              box-shadow: 0 0 5px rgba(0, 188, 212, 0.4);
              transform: scale(1);
            }
          }
          
          @keyframes rotate-pulse {
            0% {
              transform: rotate(0deg) scale(1);
            }
            25% {
              transform: rotate(5deg) scale(1.1);
            }
            50% {
              transform: rotate(0deg) scale(1);
            }
            75% {
              transform: rotate(-5deg) scale(1.1);
            }
            100% {
              transform: rotate(0deg) scale(1);
            }
          }

          @keyframes pulse-success {
            0% {
              box-shadow: 0 0 5px rgba(76, 175, 80, 0.4);
              transform: scale(1);
            }
            50% {
              box-shadow: 0 0 15px rgba(76, 175, 80, 0.8);
              transform: scale(1.05);
            }
            100% {
              box-shadow: 0 0 5px rgba(76, 175, 80, 0.4);
              transform: scale(1);
            }
          }

          /* Novas animações para ícones de origem */
          @keyframes nautilus-glow {
            0% {
              box-shadow: 0 0 8px rgba(0, 188, 212, 0.3);
              transform: scale(1);
            }
            33% {
              box-shadow: 0 0 16px rgba(0, 188, 212, 0.6);
              transform: scale(1.03);
            }
            66% {
              box-shadow: 0 0 12px rgba(38, 198, 218, 0.5);
              transform: scale(1.01);
            }
            100% {
              box-shadow: 0 0 8px rgba(0, 188, 212, 0.3);
              transform: scale(1);
            }
          }

          @keyframes user-pulse {
            0% {
              box-shadow: 0 0 4px rgba(117, 117, 117, 0.2);
              transform: scale(1);
            }
            50% {
              box-shadow: 0 0 8px rgba(117, 117, 117, 0.4);
              transform: scale(1.02);
            }
            100% {
              box-shadow: 0 0 4px rgba(117, 117, 117, 0.2);
              transform: scale(1);
            }
          }

          @keyframes spin-gradient {
            0% {
              transform: rotate(0deg);
            }
            100% {
              transform: rotate(360deg);
            }
          }

          @keyframes robot-dance {
            0% {
              transform: rotate(0deg) scale(1);
            }
            20% {
              transform: rotate(3deg) scale(1.05);
            }
            40% {
              transform: rotate(-2deg) scale(1.02);
            }
            60% {
              transform: rotate(2deg) scale(1.08);
            }
            80% {
              transform: rotate(-1deg) scale(1.03);
            }
            100% {
              transform: rotate(0deg) scale(1);
            }
          }

          @keyframes user-bounce {
            0%, 100% {
              transform: translateY(0) scale(1);
            }
            25% {
              transform: translateY(-1px) scale(1.02);
            }
            50% {
              transform: translateY(0) scale(1.01);
            }
            75% {
              transform: translateY(-0.5px) scale(1.03);
            }
          }

          @keyframes user-ripple {
            0% {
              transform: scale(1);
              opacity: 0.8;
            }
            50% {
              transform: scale(1.2);
              opacity: 0.4;
            }
            100% {
              transform: scale(1.4);
              opacity: 0;
            }
          }

          /* Animações das partículas para Nautilus */
          @keyframes particle-float-1 {
            0%, 100% {
              transform: translateY(0) translateX(0) scale(1);
              opacity: 0.7;
            }
            25% {
              transform: translateY(-3px) translateX(1px) scale(1.2);
              opacity: 1;
            }
            50% {
              transform: translateY(-1px) translateX(-1px) scale(0.8);
              opacity: 0.5;
            }
            75% {
              transform: translateY(-2px) translateX(2px) scale(1.1);
              opacity: 0.9;
            }
          }

          @keyframes particle-float-2 {
            0%, 100% {
              transform: translateY(0) translateX(0) scale(1);
              opacity: 0.8;
            }
            30% {
              transform: translateY(2px) translateX(-2px) scale(1.3);
              opacity: 0.6;
            }
            60% {
              transform: translateY(-2px) translateX(1px) scale(0.9);
              opacity: 1;
            }
            90% {
              transform: translateY(1px) translateX(-1px) scale(1.1);
              opacity: 0.7;
            }
          }

          @keyframes particle-float-3 {
            0%, 100% {
              transform: translateY(0) translateX(0) scale(1);
              opacity: 0.6;
            }
            40% {
              transform: translateY(-2px) translateX(2px) scale(1.4);
              opacity: 0.9;
            }
            70% {
              transform: translateY(1px) translateX(-2px) scale(0.7);
              opacity: 0.4;
            }
          }

          /* Novas animações para ícones super animados */
          @keyframes nautilus-container-glow {
            0% {
              box-shadow: 0 0 10px rgba(0, 188, 212, 0.4);
              transform: scale(1);
            }
            25% {
              box-shadow: 0 0 20px rgba(0, 188, 212, 0.7);
              transform: scale(1.02);
            }
            50% {
              box-shadow: 0 0 25px rgba(38, 198, 218, 0.8);
              transform: scale(1.05);
            }
            75% {
              box-shadow: 0 0 15px rgba(77, 208, 225, 0.6);
              transform: scale(1.03);
            }
            100% {
              box-shadow: 0 0 10px rgba(0, 188, 212, 0.4);
              transform: scale(1);
            }
          }

          @keyframes user-container-pulse {
            0% {
              box-shadow: 0 0 6px rgba(117, 117, 117, 0.3);
              transform: scale(1);
            }
            50% {
              box-shadow: 0 0 12px rgba(117, 117, 117, 0.6);
              transform: scale(1.03);
            }
            100% {
              box-shadow: 0 0 6px rgba(117, 117, 117, 0.3);
              transform: scale(1);
            }
          }

          @keyframes background-spin {
            0% {
              transform: rotate(0deg);
            }
            100% {
              transform: rotate(360deg);
            }
          }

          @keyframes robot-spin-bounce {
            0% {
              transform: rotate(0deg) scale(1);
            }
            25% {
              transform: rotate(90deg) scale(1.1);
            }
            50% {
              transform: rotate(180deg) scale(1);
            }
            75% {
              transform: rotate(270deg) scale(1.1);
            }
            100% {
              transform: rotate(360deg) scale(1);
            }
          }

          @keyframes user-spin-wobble {
            0% {
              transform: rotate(0deg) scale(1);
            }
            20% {
              transform: rotate(72deg) scale(1.05);
            }
            40% {
              transform: rotate(144deg) scale(0.95);
            }
            60% {
              transform: rotate(216deg) scale(1.08);
            }
            80% {
              transform: rotate(288deg) scale(0.98);
            }
            100% {
              transform: rotate(360deg) scale(1);
            }
          }

          @keyframes icon-continuous-spin {
            0% {
              transform: translate(-50%, -50%) rotate(0deg);
            }
            100% {
              transform: translate(-50%, -50%) rotate(360deg);
            }
          }

          @keyframes icon-reverse-spin {
            0% {
              transform: translate(-50%, -50%) rotate(0deg);
            }
            100% {
              transform: translate(-50%, -50%) rotate(-360deg);
            }
          }

          @keyframes orbital-motion-1 {
            0% {
              transform: translate(-50%, -50%) rotate(0deg) translateX(20px) rotate(0deg);
            }
            100% {
              transform: translate(-50%, -50%) rotate(360deg) translateX(20px) rotate(-360deg);
            }
          }

          @keyframes orbital-motion-2 {
            0% {
              transform: translate(-50%, -50%) rotate(90deg) translateX(18px) rotate(-90deg);
            }
            100% {
              transform: translate(-50%, -50%) rotate(450deg) translateX(18px) rotate(-450deg);
            }
          }

          @keyframes orbital-motion-3 {
            0% {
              transform: translate(-50%, -50%) rotate(180deg) translateX(22px) rotate(-180deg);
            }
            100% {
              transform: translate(-50%, -50%) rotate(540deg) translateX(22px) rotate(-540deg);
            }
          }

          @keyframes orbital-motion-4 {
            0% {
              transform: translate(-50%, -50%) rotate(270deg) translateX(16px) rotate(-270deg);
            }
            100% {
              transform: translate(-50%, -50%) rotate(630deg) translateX(16px) rotate(-630deg);
            }
          }

          @keyframes user-pulse-wave-1 {
            0% {
              transform: scale(1);
              opacity: 0.8;
            }
            50% {
              transform: scale(1.3);
              opacity: 0.4;
            }
            100% {
              transform: scale(1.6);
              opacity: 0;
            }
          }

          @keyframes user-pulse-wave-2 {
            0% {
              transform: scale(1);
              opacity: 0.6;
            }
            50% {
              transform: scale(1.5);
              opacity: 0.3;
            }
            100% {
              transform: scale(2);
              opacity: 0;
            }
          }

          @keyframes nautilus-mega-glow {
            0% {
              box-shadow: 0 0 10px rgba(0, 188, 212, 0.4);
              transform: scale(1);
            }
            25% {
              box-shadow: 0 0 20px rgba(0, 188, 212, 0.7);
              transform: scale(1.02);
            }
            50% {
              box-shadow: 0 0 25px rgba(38, 198, 218, 0.8);
              transform: scale(1.05);
            }
            75% {
              box-shadow: 0 0 15px rgba(77, 208, 225, 0.6);
              transform: scale(1.03);
            }
            100% {
              box-shadow: 0 0 10px rgba(0, 188, 212, 0.4);
              transform: scale(1);
            }
          }

          @keyframes user-mega-pulse {
            0% {
              box-shadow: 0 0 6px rgba(117, 117, 117, 0.3);
              transform: scale(1);
            }
            50% {
              box-shadow: 0 0 12px rgba(117, 117, 117, 0.6);
              transform: scale(1.03);
            }
            100% {
              box-shadow: 0 0 6px rgba(117, 117, 117, 0.3);
              transform: scale(1);
            }
          }

          @keyframes mega-spin-gradient {
            0% {
              transform: rotate(0deg);
            }
            100% {
              transform: rotate(360deg);
            }
          }

          @keyframes user-ripple-wave {
            0% {
              transform: scale(1);
              opacity: 0.6;
            }
            50% {
              transform: scale(1.3);
              opacity: 0.3;
            }
            100% {
              transform: scale(1.6);
              opacity: 0;
            }
          }

          @keyframes robot-mega-dance {
            0% {
              transform: rotate(0deg) scale(1);
            }
            15% {
              transform: rotate(4deg) scale(1.08);
            }
            30% {
              transform: rotate(-3deg) scale(1.05);
            }
            45% {
              transform: rotate(5deg) scale(1.12);
            }
            60% {
              transform: rotate(-2deg) scale(1.06);
            }
            75% {
              transform: rotate(3deg) scale(1.09);
            }
            90% {
              transform: rotate(-1deg) scale(1.03);
            }
            100% {
              transform: rotate(0deg) scale(1);
            }
          }

          @keyframes user-mega-bounce {
            0%, 100% {
              transform: translateY(0) scale(1);
            }
            20% {
              transform: translateY(-2px) scale(1.05);
            }
            40% {
              transform: translateY(0) scale(1.02);
            }
            60% {
              transform: translateY(-1px) scale(1.08);
            }
            80% {
              transform: translateY(0) scale(1.04);
            }
          }

          @keyframes mega-particle-float-1 {
            0%, 100% {
              transform: translateY(0) translateX(0) scale(1);
              opacity: 0.7;
            }
            20% {
              transform: translateY(-4px) translateX(2px) scale(1.3);
              opacity: 1;
            }
            40% {
              transform: translateY(-2px) translateX(-2px) scale(0.8);
              opacity: 0.5;
            }
            60% {
              transform: translateY(-3px) translateX(3px) scale(1.2);
              opacity: 0.9;
            }
            80% {
              transform: translateY(-1px) translateX(-1px) scale(1.1);
              opacity: 0.6;
            }
          }

          @keyframes mega-particle-float-2 {
            0%, 100% {
              transform: translateY(0) translateX(0) scale(1);
              opacity: 0.8;
            }
            25% {
              transform: translateY(3px) translateX(-3px) scale(1.4);
              opacity: 0.6;
            }
            50% {
              transform: translateY(-3px) translateX(2px) scale(0.9);
              opacity: 1;
            }
            75% {
              transform: translateY(2px) translateX(-2px) scale(1.2);
              opacity: 0.7;
            }
          }

          @keyframes mega-particle-float-3 {
            0%, 100% {
              transform: translateY(0) translateX(0) scale(1);
              opacity: 0.6;
            }
            33% {
              transform: translateY(-3px) translateX(3px) scale(1.5);
              opacity: 0.9;
            }
            66% {
              transform: translateY(2px) translateX(-3px) scale(0.7);
              opacity: 0.4;
            }
          }

          @keyframes energy-ring-spin {
            0% {
              transform: rotate(0deg);
            }
            100% {
              transform: rotate(360deg);
            }
          }

          @keyframes user-energy-wave-1 {
            0% {
              transform: scale(1);
              opacity: 0.8;
            }
            50% {
              transform: scale(1.4);
              opacity: 0.4;
            }
            100% {
              transform: scale(1.8);
              opacity: 0;
            }
          }

          @keyframes user-energy-wave-2 {
            0% {
              transform: scale(1);
              opacity: 0.6;
            }
            50% {
              transform: scale(1.6);
              opacity: 0.3;
            }
            100% {
              transform: scale(2.2);
              opacity: 0;
            }
          }

          @keyframes user-energy-wave-3 {
            0% {
              transform: scale(1);
              opacity: 0.4;
            }
            50% {
              transform: scale(1.8);
              opacity: 0.2;
            }
            100% {
              transform: scale(2.6);
              opacity: 0;
            }
          }

          @keyframes status-blink-green {
            0%, 100% {
              opacity: 1;
              transform: scale(1);
            }
            50% {
              opacity: 0.6;
              transform: scale(1.2);
            }
          }

          @keyframes status-blink-orange {
            0%, 100% {
              opacity: 1;
              transform: scale(1);
            }
            50% {
              opacity: 0.7;
              transform: scale(1.1);
            }
          }

          /* Efeito hover global para ícones animados */
          .animated-origin-icon:hover {
            animation-play-state: paused !important;
          }

          .animated-origin-icon:hover .icon-content {
            animation: icon-hover-dance 0.6s ease-in-out !important;
          }

          @keyframes icon-hover-dance {
            0%, 100% {
              transform: rotate(0deg) scale(1);
            }
            25% {
              transform: rotate(5deg) scale(1.1);
            }
            50% {
              transform: rotate(-3deg) scale(1.05);
            }
            75% {
              transform: rotate(3deg) scale(1.08);
            }
          }
        `}
      </style>

      <Paper sx={{ p: 2.5, height: 380 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '1.1rem' }}>
              <TrendingUp color="primary" sx={{ fontSize: 20 }} />
              📊 Posições Abertas ({positions.length})
            </Typography>
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              mt: 0.5
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <SmartToy sx={{ fontSize: 14, color: '#00bcd4' }} />
                <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
                  Nautilus: {positions.filter(p => detectOperationOrigin(p).isNautilus).length}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Person sx={{ fontSize: 14, color: '#757575' }} />
                <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
                  Manual: {positions.filter(p => detectOperationOrigin(p).isManual).length}
                </Typography>
              </Box>
            </Box>
          </Box>

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
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', paddingLeft: '69px' }}>
                  <span style={{
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    display: 'block',
                    padding: '4px 0'
                  }}>
                    Origem & Ativo
                  </span>
                </TableCell>
                <TableCell sx={{ fontSize: '0.8rem', fontWeight: 'bold', textAlign: 'center', minWidth: '120px' }}>
                  <Tooltip title="Indicadores de Takes atingidos (🎯)" arrow>
                    <span style={{ cursor: 'help' }}>Takes</span>
                  </Tooltip>
                </TableCell>
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
                const { isNautilus, isManual, icon, tooltip, color, bgColor } = detectOperationOrigin(position);
                const origin = { isNautilus, isManual, icon, tooltip, color, bgColor };
                return (
                  <TableRow
                    key={index}
                    hover
                    sx={{
                      '& td': {
                        py: 1.5, // Aumenta o padding vertical das células
                        borderBottom: '1px solid rgba(255, 255, 255, 0.05)'
                      }
                    }}
                  >
                    <TableCell>
                      <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1.5,
                        py: 0.5
                      }}>
                        <Box sx={{
                          width: '45px',
                          textAlign: 'left',
                          flexShrink: 0
                        }}>
                          <Typography variant="body2" sx={{
                            color: 'text.secondary',
                            fontSize: '0.75rem',
                            fontWeight: '500'
                          }}>
                            {position.leverage}x
                          </Typography>
                        </Box>

                        <Box sx={{ flexShrink: 0 }}>
                          <SuperAnimatedOriginIcon origin={origin} />
                        </Box>

                        <Typography variant="body2" sx={{
                          fontWeight: 'bold',
                          fontSize: '0.85rem',
                          color: 'text.primary'
                        }}>
                          {position.symbol}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <TakesIndicator takesHit={position.takes_hit || 0} />
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