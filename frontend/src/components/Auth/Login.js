import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  Grid
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Instagram,
  YouTube,
  Telegram as TelegramIcon,
  Close,
  Psychology
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import FinanceBackground from './FinanceBackground';



const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showWebhookEmailModal, setShowWebhookEmailModal] = useState(false);
  const [webhookEmail, setWebhookEmail] = useState('');
  const [webhookEmailError, setWebhookEmailError] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [inviteError, setInviteError] = useState('');
  const [inviteSuccess, setInviteSuccess] = useState(false);
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  // Detectar retorno do pagamento e redirecionar automaticamente
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const paymentSuccess = urlParams.get('payment_success');
    const sessionId = urlParams.get('session_id');
    
    if (paymentSuccess === 'true' || sessionId) {
      // Pagamento foi concluído com sucesso
      toast.success('🎉 Pagamento confirmado! Redirecionando para o cadastro...', {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      
      // Redirecionar para formulário de registro após um breve delay
      setTimeout(() => {
        navigate('/register?payment_confirmed=true');
      }, 2000);
    }
  }, [location.search, navigate]);

  // Verificar se há mudança na URL (usuário voltou da página de pagamento)
  useEffect(() => {
    const handlePopState = () => {
      // Verifica se o usuário voltou da página de pagamento
      const urlParams = new URLSearchParams(window.location.search);
      const returnedFromPayment = urlParams.get('returned_from_payment');
      
      if (returnedFromPayment === 'true') {
        // Mostrar modal de confirmação e redirecionar
        toast.success('✅ Retornando do pagamento! Redirecionando para o cadastro...');
        setTimeout(() => {
          navigate('/register?payment_completed=true');
        }, 1500);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData.email, formData.password);
      toast.success('Login realizado com sucesso!');
    } catch (error) {
      // Filtrar erros de verificação de sessão para não confundir o usuário
      if (error.message && error.message.includes('verificação de sessão')) {
        console.log('Erro de verificação de sessão ignorado:', error.message);
        return;
      }
      
      const errorMessage = error.response?.data?.message || error.message || 'Erro ao fazer login. Verifique suas credenciais.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleOpenPaymentModal = () => {
    setShowPaymentModal(true);
  };

  const handleClosePaymentModal = () => {
    setShowPaymentModal(false);
  };

  const handlePaymentClick = (link) => {
    // Adicionar parâmetro para detectar retorno
    const returnUrl = `${window.location.origin}/login?returned_from_payment=true`;
    const enhancedLink = `${link}?success_url=${encodeURIComponent(returnUrl)}&cancel_url=${encodeURIComponent(returnUrl)}`;
    
    window.open(enhancedLink, '_blank', 'noopener,noreferrer');
  };

  const handleWebhookTestClick = () => {
    setShowPaymentModal(false);
    setShowWebhookEmailModal(true);
    setWebhookEmail('');
    setWebhookEmailError('');
  };

  const handleCloseWebhookEmailModal = () => {
    setShowWebhookEmailModal(false);
    setWebhookEmail('');
    setWebhookEmailError('');
  };

  const handleWebhookEmailSubmit = () => {
    if (!webhookEmail.trim()) {
      setWebhookEmailError('Por favor, digite seu email.');
      return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(webhookEmail)) {
      setWebhookEmailError('Por favor, digite um email válido.');
      return;
    }

    // Limpar erros e fechar modal
    setWebhookEmailError('');
    setShowWebhookEmailModal(false);
    
    // Armazenar email para usar na tela de confirmação
    localStorage.setItem('payment_email', webhookEmail);
    
    // URL de retorno personalizada para nossa nova tela de confirmação
    const returnUrl = `${window.location.origin}/payment-success`;
    const cancelUrl = `${window.location.origin}/login`;
    const enhancedLink = `https://checkout.grupobigwhale.com/b/cNi5kF4wa19eg6I60bgnK04?success_url=${encodeURIComponent(returnUrl)}&cancel_url=${encodeURIComponent(cancelUrl)}`;
    
    // Redirecionar para o pagamento
    window.open(enhancedLink, '_blank', 'noopener,noreferrer');
    
    // Mostrar toast de sucesso
    toast.success(`📧 Email ${webhookEmail} registrado! Prossiga com o pagamento.`);
  };

  const handleOpenInviteModal = () => setShowInviteModal(true);
  const handleCloseInviteModal = () => setShowInviteModal(false);

  const handleValidateInvite = () => {
    if (inviteCode.trim() === 'Bigwhale81#') {
      setInviteSuccess(true);
      setInviteError('');
    } else {
      setInviteError('Código de convite inválido.');
      setInviteSuccess(false);
    }
  };



  // Efeito para animação de digitação do título
  useEffect(() => {
    const text = 'Nautilus';
    let currentIndex = 0;
    let typingInterval;
    let restartTimeout;

    const typeText = () => {
      setIsTyping(true);
      setDisplayedText('');
      currentIndex = 0;
      
      typingInterval = setInterval(() => {
        if (currentIndex < text.length) {
          setDisplayedText(text.slice(0, currentIndex + 1));
          currentIndex++;
        } else {
          clearInterval(typingInterval);
          setIsTyping(false);
          
          // Reinicia a animação após 10 segundos
          restartTimeout = setTimeout(() => {
            typeText();
          }, 10000);
        }
      }, 150); // Velocidade de digitação
    };

    // Inicia a primeira animação
    typeText();

    // Cleanup
    return () => {
      clearInterval(typingInterval);
      clearTimeout(restartTimeout);
    };
  }, []);

  // 3. Função para redirecionar para registro (ajuste: redirecionar automaticamente ao validar)
  useEffect(() => {
    if (inviteSuccess) {
      setShowInviteModal(false);
      setTimeout(() => {
        setInviteCode('');
        setInviteError('');
        setInviteSuccess(false);
        window.location.href = '/register';
      }, 200);
    }
  }, [inviteSuccess]);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2
      }}
    >
      <FinanceBackground />
      <Container maxWidth="sm" sx={{ position: 'relative', zIndex: 2 }}>
        <Paper
          elevation={24}
          className="login-paper"
          sx={{
            p: 4,
            borderRadius: 3,
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.3)',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '1px',
              background: 'linear-gradient(90deg, transparent, rgba(102, 255, 204, 0.2), transparent)'
            }
          }}
        >
          {/* Logo e Título */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography
              variant="h4"
              component="h1"
              sx={{
                color: '#66FFCC',
                fontWeight: 'bold',
                textShadow: '0 0 10px rgba(102, 255, 204, 0.3)',
                mb: 1,
                minHeight: '2.5rem',
                fontFamily: 'monospace',
                letterSpacing: '0.1em'
              }}
            >
              {displayedText}
              {isTyping && (
                <span
                  style={{
                    animation: 'blink 1s infinite',
                    marginLeft: '2px'
                  }}
                >
                  |
                </span>
              )}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
              <Psychology 
                sx={{
                  color: '#66FFCC',
                  fontSize: '1.5rem',
                  mr: 1,
                  animation: 'pulse 2s infinite'
                }}
              />
              <Typography
                variant="subtitle1"
                sx={{
                  color: 'rgba(255, 255, 255, 0.7)'
                }}
              >
                Inteligência operando, você vivendo o resultado.
              </Typography>
            </Box>
          </Box>
          <style>
             {`
               @keyframes blink {
                 0%, 50% { opacity: 1; }
                 51%, 100% { opacity: 0; }
               }
               @keyframes pulse {
                 0% { transform: scale(1); opacity: 0.8; }
                 50% { transform: scale(1.1); opacity: 1; }
                 100% { transform: scale(1); opacity: 0.8; }
               }
             `}
           </style>

          {/* Formulário */}
          <form onSubmit={handleSubmit}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              sx={{
                mb: 2,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: 'rgba(102, 255, 204, 0.2)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(102, 255, 204, 0.4)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#66FFCC',
                  },
                },
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                },
                '& .MuiInputBase-input': {
                  color: '#fff',
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email sx={{ color: 'rgba(102, 255, 204, 0.5)' }} />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Senha"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange}
              required
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: 'rgba(102, 255, 204, 0.2)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(102, 255, 204, 0.4)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#66FFCC',
                  },
                },
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                },
                '& .MuiInputBase-input': {
                  color: '#fff',
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock sx={{ color: 'rgba(102, 255, 204, 0.5)' }} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={togglePasswordVisibility}
                      edge="end"
                      sx={{ color: 'rgba(102, 255, 204, 0.5)' }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              disabled={loading}
              sx={{
                mb: 2,
                bgcolor: '#66FFCC',
                color: '#000',
                '&:hover': {
                  bgcolor: '#4DFFB8',
                },
                '&:disabled': {
                  bgcolor: 'rgba(102, 255, 204, 0.3)',
                },
              }}
            >
              {loading ? <CircularProgress size={24} /> : 'Entrar'}
            </Button>
          </form>

          {/* Seção de Planos */}
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="h6" sx={{ mb: 2, color: 'rgba(255, 255, 255, 0.9)' }}>
              Escolha seu Plano
            </Typography>
            <Grid container spacing={2} justifyContent="center">
              <Grid item>
                <Button
                  variant="outlined"
                  onClick={handleOpenPaymentModal}
                  className="button-plano"
                >
                  Assinatura
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  onClick={handleOpenInviteModal}
                  className="button-plano"
                >
                  Convite
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="outlined"
                  disabled
                  className="button-plano"
                  sx={{
                    '& .MuiTypography-root': {
                      color: '#ff0000 !important',
                      fontSize: '0.7rem',
                      position: 'absolute',
                      top: '-8px',
                      right: '-8px'
                    }
                  }}
                >
                  Recarregar
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#ff0000',
                      display: 'block',
                      textAlign: 'center',
                      mt: -2,
                      mb: 3,
                      fontSize: '0.9rem',
                      position: 'relative',
                      zIndex: 3
                    }}
                  >
                    Em Breve
                  </Typography>
                </Button>
              </Grid>
            </Grid>
          </Box>

          {/* Redes Sociais */}
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography
              variant="body2"
              sx={{
                mb: 2,
                color: 'rgba(255, 255, 255, 0.7)'
              }}
            >
              Siga-nos nas redes sociais
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
              <IconButton
                component="a"
                href="https://www.instagram.com/bigwhale_oficial?igsh=MXh6aHVjZWtyY240YQ=="
                target="_blank"
                sx={{ color: 'rgba(102, 255, 204, 0.5)' }}
              >
                <Instagram />
              </IconButton>
              <IconButton
                component="a"
                href="https://www.youtube.com/@grupobigwhale_of"
                target="_blank"
                sx={{ color: 'rgba(102, 255, 204, 0.5)' }}
              >
                <YouTube />
              </IconButton>
              <IconButton
                component="a"
                href="https://t.me/grupobigwhale_Of"
                target="_blank"
                sx={{ color: 'rgba(102, 255, 204, 0.5)' }}
              >
                <TelegramIcon />
              </IconButton>
            </Box>
            
            {/* Seção Bitget */}
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography
                variant="body2"
                sx={{
                  color: '#C0C0C0',
                  mb: 2,
                  fontSize: '0.9rem',
                  lineHeight: 1.5
                }}
              >
                Caso ainda não tenha conta na <span style={{textDecoration: 'underline', fontWeight: 'bold', color: '#66FFCC', fontSize: '1.1em'}}>Bitget</span>, se cadastre sendo nosso Parceiro e receba 10% de Cashback em todas as taxas. Futuros e Spot de forma vitalícia.
              </Typography>
              <Button
                variant="contained"
                component="a"
                href="https://partner.bitget.com/bg/sxz4yh2u"
                target="_blank"
                sx={{
                  background: 'linear-gradient(135deg, #66FFCC 0%, rgba(102, 255, 204, 0.8) 100%)',
                  color: '#000',
                  fontWeight: 'bold',
                  px: 4,
                  py: 1.5,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontSize: '1rem',
                  '&:hover': {
                    background: 'linear-gradient(135deg, rgba(102, 255, 204, 0.9) 0%, #66FFCC 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(102, 255, 204, 0.3)'
                  },
                  transition: 'all 0.3s ease'
                }}
              >
                Cadastre-se
              </Button>
            </Box>
          </Box>
        </Paper>
      </Container>

      {/* Modal de Opções de Pagamento */}
      <Dialog
        open={showPaymentModal}
        onClose={handleClosePaymentModal}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'hsla(0, 0.00%, 0.00%, 0.93) !important',
            border: '2px solid #C0C0C0',
            borderRadius: 4,
            boxShadow: '0 4px 32px 0 rgba(192,192,192,0.12)',
            color: '#C0C0C0',
            p: 3
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid rgba(102, 255, 204, 0.1)',
          pb: 2,
          fontWeight: 600,
          color: '#66FFCC',
          fontSize: '1.3rem'
        }}>
          Planos de Assinatura
          <IconButton onClick={handleClosePaymentModal} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ py: 4, px: 5, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2.5 }}>
          <Button
            variant="contained"
            onClick={() => handlePaymentClick('https://checkout.grupobigwhale.com/b/14A00l6Ei05a4o04W7gnK02')}
            className="button-plano"
            sx={{
              width: '100%',
              maxWidth: 400,
              py: 2.5,
              mt: 3,
              mb: 2.5,
              fontSize: '1.3rem',
              fontWeight: 800,
              letterSpacing: 0.5,
              transition: 'all 0.3s',
            }}
          >
            Assinatura Mensal
          </Button>
          <Button
            variant="contained"
            onClick={() => handlePaymentClick('https://checkout.grupobigwhale.com/b/4gM14pfaO6tyg6IfALgnK03')}
            className="button-plano"
            sx={{
              width: '100%',
              maxWidth: 400,
              py: 2.5,
              fontSize: '1.3rem',
              fontWeight: 800,
              letterSpacing: 0.5,
              transition: 'all 0.3s',
            }}
          >
            Assinatura Anual
          </Button>
          <Button
            variant="contained"
            onClick={handleWebhookTestClick}
            className="button-plano"
            sx={{
              width: '100%',
              maxWidth: 400,
              py: 2.5,
              fontSize: '1.3rem',
              fontWeight: 800,
              letterSpacing: 0.5,
              transition: 'all 0.3s',
              backgroundColor: '#FFD700',
              color: '#000',
              '&:hover': {
                backgroundColor: '#FFA500',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(255, 215, 0, 0.3)'
              }
            }}
          >
            🧪 Teste Webhook
          </Button>
        </DialogContent>
      </Dialog>

      {/* Modal de Email para Teste Webhook */}
      <Dialog
        open={showWebhookEmailModal}
        onClose={handleCloseWebhookEmailModal}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            background: 'hsla(0, 0.00%, 0.00%, 0.93) !important',
            border: '2px solid #FFD700',
            borderRadius: 4,
            boxShadow: '0 4px 32px 0 rgba(255, 215, 0, 0.12)',
            color: '#C0C0C0',
            p: 3
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid rgba(255, 215, 0, 0.1)',
          pb: 2,
          fontWeight: 600,
          color: '#FFD700',
          fontSize: '1.3rem'
        }}>
          🧪 Teste Webhook
          <IconButton onClick={handleCloseWebhookEmailModal} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ py: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.85)', mb: 2, textAlign: 'center' }}>
            Para prosseguir com o teste webhook, digite seu email:
          </Typography>
          <TextField
            label="Seu Email"
            variant="outlined"
            type="email"
            value={webhookEmail}
            onChange={(e) => setWebhookEmail(e.target.value)}
            fullWidth
            sx={{
              input: { color: 'white' },
              label: { color: 'rgba(255,255,255,0.7)' },
              mb: 1,
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                borderRadius: 2,
                '& fieldset': {
                  borderColor: 'rgba(255, 215, 0, 0.3)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 215, 0, 0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#FFD700',
                  boxShadow: '0 0 0 2px rgba(255, 215, 0, 0.1)',
                },
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Email sx={{ color: 'rgba(255, 215, 0, 0.5)' }} />
                </InputAdornment>
              ),
            }}
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            autoFocus
            onKeyDown={(e) => { if (e.key === 'Enter') handleWebhookEmailSubmit(); }}
          />
          {webhookEmailError && (
            <Typography variant="body2" sx={{ color: '#ff6464', mb: 1 }}>{webhookEmailError}</Typography>
          )}
          <Button
            variant="contained"
            onClick={handleWebhookEmailSubmit}
            sx={{
              mt: 2,
              backgroundColor: '#FFD700',
              color: '#000',
              fontWeight: 'bold',
              '&:hover': {
                backgroundColor: '#FFA500',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(255, 215, 0, 0.3)'
              },
              transition: 'all 0.3s'
            }}
            fullWidth
          >
            Continuar com o Pagamento
          </Button>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', textAlign: 'center', mt: 2 }}>
            Modo sem cobrança de comissão. Insira este email durante o processo de pagamento.
          </Typography>
        </DialogContent>
      </Dialog>

      {/* Modal de Convite */}
      <Dialog
        open={showInviteModal}
        onClose={() => {
          setInviteCode('');
          setInviteError('');
          setInviteSuccess(false);
          handleCloseInviteModal();
        }}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            background: 'hsla(0, 0.00%, 0.00%, 0.93) !important',
            border: '2px solid #C0C0C0',
            borderRadius: 4,
            boxShadow: '0 4px 32px 0 rgba(192,192,192,0.12)',
            color: '#C0C0C0',
            p: 3
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid rgba(102, 255, 204, 0.1)',
          pb: 2,
          fontWeight: 600,
          color: '#66FFCC',
          fontSize: '1.3rem'
        }}>
          Registro por Convite
          <IconButton onClick={handleCloseInviteModal} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ py: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.85)', mb: 2, textAlign: 'center' }}>
            Digite o código de convite para liberar o cadastro:
          </Typography>
          <TextField
            label="Código de Convite"
            variant="outlined"
            value={inviteCode}
            onChange={e => setInviteCode(e.target.value)}
            fullWidth
            sx={{
              input: { color: 'white' },
              label: { color: 'rgba(255,255,255,0.7)' },
              mb: 1,
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                borderRadius: 2,
                '& fieldset': {
                  borderColor: 'rgba(102, 255, 204, 0.3)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(102, 255, 204, 0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#66FFCC',
                  boxShadow: '0 0 0 2px rgba(102, 255, 204, 0.1)',
                },
              },
            }}
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            autoFocus
            onKeyDown={e => { if (e.key === 'Enter') handleValidateInvite(); }}
            disabled={inviteSuccess}
          />
          {inviteError && (
            <Typography variant="body2" sx={{ color: '#ff6464', mb: 1 }}>{inviteError}</Typography>
          )}
          {inviteSuccess ? (
            <Typography variant="h6" sx={{ color: '#66FFCC', mt: 2, textAlign: 'center' }}>
              Código válido! Redirecionando...
            </Typography>
          ) : (
            <Button
              variant="contained"
              onClick={handleValidateInvite}
              className="button-validar-codigo"
              sx={{ mt: 2 }}
              fullWidth
            >
              Validar Código
            </Button>
          )}
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', textAlign: 'center', mt: 2 }}>
            O código de convite é pessoal e intransferível. Após validar, siga as regras já exibidas na tela de registro.
          </Typography>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default Login;