import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  CircularProgress,
  Container,
  InputAdornment,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Grid
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Person,
  Check,
  Close,
  Api
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import authService from '../../services/authService';
import logger from '../../utils/logger';
import FinanceBackground from './FinanceBackground';

const RegisterPayment = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    bitget_api_key: '',
    bitget_api_secret: '',
    bitget_passphrase: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showApiSecret, setShowApiSecret] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordValidation, setPasswordValidation] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false
  });

  // Detectar parâmetros da URL e preencher email automaticamente
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get('email');
    
    if (email) {
      setFormData(prev => ({
        ...prev,
        email: email
      }));
      
      // Mostrar mensagem de sucesso
      toast.success('🎉 Pagamento confirmado! Email preenchido automaticamente.', {
        position: "top-center",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      
      console.log('✅ Email preenchido automaticamente:', email);
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (name === 'password') {
      validatePassword(value);
    }

    if (error) {
      setError('');
    }
  };

  const validatePassword = (password) => {
    setPasswordValidation({
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[@$!%*?&_\-]/.test(password)
    });
  };

  const isPasswordValid = () => {
    return Object.values(passwordValidation).every(Boolean);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const { full_name, email, password, confirmPassword, bitget_api_key, bitget_api_secret, bitget_passphrase } = formData;

    // Validação dos campos obrigatórios
    let requiredFields = [full_name, email, password, confirmPassword, bitget_api_key, bitget_api_secret, bitget_passphrase];
    
    if (requiredFields.some(field => !field)) {
      setError('Todos os campos são obrigatórios.');
      setLoading(false);
      return;
    }

    if (!authService.validateEmail(email)) {
      setError('Formato de email inválido');
      setLoading(false);
      return;
    }

    if (!isPasswordValid()) {
      setError('A senha não atende aos requisitos de complexidade');
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('As senhas não coincidem');
      setLoading(false);
      return;
    }

    try {
      const registrationData = {
        full_name,
        email,
        password,
        bitget_api_key,
        bitget_api_secret,
        bitget_passphrase,
        paid_user: true, // HARDCODED: Sempre verdadeiro para este formulário
      };

      logger.secure('Iniciando processo de registro (pagamento)');
      const response = await authService.register(registrationData);
      logger.secure('Registro processado com sucesso (pagamento)');
      
      const responseData = response.data || response;
      
      if (responseData && responseData.nautilus_data_sent) {
        toast.success('Conta criada com sucesso! Dados enviados para o sistema Nautilus. Faça login para continuar.', {
          autoClose: 8000,
          position: "top-center"
        });
      }
      
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (error) {
      logger.error('Erro no registro (pagamento):', error);
      
      // Mensagens de erro mais detalhadas
      if (error.response) {
        if (error.response.status === 409) {
          setError(error.response.data?.message || 'Este email ou credenciais Bitget já estão registrados. Tente fazer login ou use outros dados.');
        } else if (error.response.status === 400) {
          const errorMsg = error.response.data?.message || 'Dados inválidos fornecidos.';
          if (errorMsg.includes('API')) {
            setError(`Erro nas credenciais da Bitget: ${errorMsg}`);
          } else {
            setError(errorMsg);
          }
        } else if (error.response.status === 422) {
          setError('Erro de validação: Verifique se todos os campos estão preenchidos corretamente.');
        } else if (error.response.status >= 500) {
          setError('Erro interno do servidor. Tente novamente em alguns minutos.');
        } else {
          setError(error.response.data?.message || 'Erro ao criar conta. Tente novamente.');
        }
      } else {
        setError('Erro ao criar conta. Verifique sua conexão e tente novamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  const ValidationIcon = ({ isValid }) => (
    <ListItemIcon sx={{ minWidth: 35 }}>
      {isValid ? <Check sx={{ color: 'green' }} /> : <Close sx={{ color: 'red' }} />}
    </ListItemIcon>
  );

  return (
    <>
    <FinanceBackground />
    <Container component="main" maxWidth="md" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          width: '100%',
          maxWidth: '900px',
          p: 2,
        }}
      >
        <Paper
          elevation={6}
          sx={{
            p: { xs: 3, md: 4 },
            width: '100%',
            maxHeight: '85vh',
            overflowY: 'auto',
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            borderRadius: '15px',
            border: '1px solid rgba(192, 192, 192, 0.3)',
            backdropFilter: 'blur(5px)',
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              backgroundColor: 'rgba(0,0,0,0.1)',
              borderRadius: '10px',
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: 'rgba(192,192,192,0.3)',
              borderRadius: '10px',
            },
          }}
        >
          <Typography component="h1" variant="h4" sx={{ mb: 2, textAlign: 'center', color: '#C0C0C0', fontWeight: 'bold' }}>
            Nautilus Automação
          </Typography>
          <Typography variant="h6" sx={{ mb: 3, textAlign: 'center', color: '#C0C0C0' }}>
            Crie sua conta de trading
          </Typography>

          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            
            <>
              {/* Seção de Dados Pessoais */}
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    name="full_name"
                    label="Nome Completo *"
                    value={formData.full_name}
                    onChange={handleChange}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Person sx={{ color: '#C0C0C0' }} />
                        </InputAdornment>
                      ),
                      sx: { color: '#C0C0C0', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#C0C0C0' } }
                    }}
                    InputLabelProps={{
                      sx: { color: '#C0C0C0' }
                    }}
                    sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(192, 192, 192, 0.5)' }, '&:hover fieldset': { borderColor: '#C0C0C0' } } }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    name="email"
                    label="Email *"
                    value={formData.email}
                    onChange={handleChange}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Email sx={{ color: '#C0C0C0' }} />
                        </InputAdornment>
                      ),
                      sx: { color: '#C0C0C0', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#C0C0C0' } }
                    }}
                    InputLabelProps={{
                      sx: { color: '#C0C0C0' }
                    }}
                    sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(192, 192, 192, 0.5)' }, '&:hover fieldset': { borderColor: '#C0C0C0' } } }}
                  />
                </Grid>
              </Grid>

              {/* Seção de Senhas */}
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    name="password"
                    label="Senha *"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleChange}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock sx={{ color: '#C0C0C0' }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                            sx={{ color: '#C0C0C0' }}
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                      sx: { color: '#C0C0C0', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#C0C0C0' } }
                    }}
                    InputLabelProps={{
                      sx: { color: '#C0C0C0' }
                    }}
                    sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(192, 192, 192, 0.5)' }, '&:hover fieldset': { borderColor: '#C0C0C0' } } }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    name="confirmPassword"
                    label="Confirmar Senha *"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock sx={{ color: '#C0C0C0' }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            edge="end"
                            sx={{ color: '#C0C0C0' }}
                          >
                            {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                      sx: { color: '#C0C0C0', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#C0C0C0' } }
                    }}
                    InputLabelProps={{
                      sx: { color: '#C0C0C0' }
                    }}
                    sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(192, 192, 192, 0.5)' }, '&:hover fieldset': { borderColor: '#C0C0C0' } } }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <List dense sx={{ color: '#C0C0C0', display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <ListItem disableGutters sx={{ width: 'auto', minWidth: '180px' }}>
                      <ValidationIcon isValid={passwordValidation.length} />
                      <ListItemText primary="Mínimo de 8 caracteres" />
                    </ListItem>
                    <ListItem disableGutters sx={{ width: 'auto', minWidth: '160px' }}>
                      <ValidationIcon isValid={passwordValidation.uppercase} />
                      <ListItemText primary="Uma letra maiúscula" />
                    </ListItem>
                    <ListItem disableGutters sx={{ width: 'auto', minWidth: '160px' }}>
                      <ValidationIcon isValid={passwordValidation.lowercase} />
                      <ListItemText primary="Uma letra minúscula" />
                    </ListItem>
                    <ListItem disableGutters sx={{ width: 'auto', minWidth: '100px' }}>
                      <ValidationIcon isValid={passwordValidation.number} />
                      <ListItemText primary="Um número" />
                    </ListItem>
                    <ListItem disableGutters sx={{ width: 'auto', minWidth: '200px' }}>
                      <ValidationIcon isValid={passwordValidation.special} />
                      <ListItemText primary="Um caractere especial (@$!%*?&_-)" />
                    </ListItem>
                  </List>
                </Grid>
              </Grid>

              {/* Seção de Credenciais Bitget */}
              <Typography variant="h6" sx={{ mt: 3, mb: 2, color: '#C0C0C0', textAlign: 'center' }}>
                🔑 Credenciais da API Bitget
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    name="bitget_api_key"
                    label="Bitget API Key *"
                    value={formData.bitget_api_key}
                    onChange={handleChange}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Api sx={{ color: '#C0C0C0' }} />
                        </InputAdornment>
                      ),
                      sx: { color: '#C0C0C0', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#C0C0C0' } }
                    }}
                    InputLabelProps={{
                      sx: { color: '#C0C0C0' }
                    }}
                    sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(192, 192, 192, 0.5)' }, '&:hover fieldset': { borderColor: '#C0C0C0' } } }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    name="bitget_api_secret"
                    label="Bitget API Secret *"
                    type={showApiSecret ? 'text' : 'password'}
                    value={formData.bitget_api_secret}
                    onChange={handleChange}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Api sx={{ color: '#C0C0C0' }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowApiSecret(!showApiSecret)}
                            edge="end"
                            sx={{ color: '#C0C0C0' }}
                          >
                            {showApiSecret ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                      sx: { color: '#C0C0C0', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#C0C0C0' } }
                    }}
                    InputLabelProps={{
                      sx: { color: '#C0C0C0' }
                    }}
                    sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(192, 192, 192, 0.5)' }, '&:hover fieldset': { borderColor: '#C0C0C0' } } }}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    name="bitget_passphrase"
                    label="Bitget Passphrase *"
                    value={formData.bitget_passphrase}
                    onChange={handleChange}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock sx={{ color: '#C0C0C0' }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title="Passphrase da sua API Bitget (obrigatório para autenticação)">
                            <Api sx={{ color: '#C0C0C0' }} />
                          </Tooltip>
                        </InputAdornment>
                      ),
                      sx: { color: '#C0C0C0', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#C0C0C0' } }
                    }}
                    InputLabelProps={{
                      sx: { color: '#C0C0C0' }
                    }}
                    sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(192, 192, 192, 0.5)' }, '&:hover fieldset': { borderColor: '#C0C0C0' } } }}
                  />
                </Grid>
              </Grid>

              {/* Aviso de segurança */}
              <Alert severity="info" sx={{ mt: 2, mb: 2, backgroundColor: 'rgba(0, 0, 0, 0.6)', color: '#C0C0C0', border: '1px solid rgba(192, 192, 192, 0.3)' }}>
                <Typography variant="caption" sx={{ color: '#C0C0C0' }}>
                  🔒 Suas credenciais da API são criptografadas com AES-256 e armazenadas com segurança.
                  Nunca compartilhe suas chaves de API com terceiros.
                </Typography>
              </Alert>

              {/* Aviso de pagamento aprovado */}
              <Alert severity="success" sx={{ mt: 2, mb: 2, backgroundColor: 'rgba(0, 255, 0, 0.1)', color: '#00FF00', border: '1px solid rgba(0, 255, 0, 0.3)' }}>
                <Typography variant="caption" sx={{ color: '#00FF00' }}>
                  💰 Pagamento Aprovado! Você pode prosseguir com o cadastro.
                </Typography>
              </Alert>
            </>

            {/* Botão de envio */}
            <Box sx={{ mt: 3, mb: 2 }}>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading || !isPasswordValid()}
                sx={{
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 'bold',
                  background: 'rgba(0, 0, 0, 0.8)',
                  border: '1px solid rgba(192, 192, 192, 0.3)',
                  color: '#C0C0C0',
                  '&:hover': {
                    background: 'rgba(0, 0, 0, 0.9)',
                    border: '1px solid #C0C0C0'
                  },
                  '&:disabled': {
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(192, 192, 192, 0.1)',
                    color: 'rgba(192, 192, 192, 0.3)'
                  },
                }}
              >
                {loading ? (
                  <CircularProgress size={24} sx={{ color: '#C0C0C0' }} />
                ) : (
                  'Criar Conta'
                )}
              </Button>
            </Box>

            {/* Link para login */}
            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2" sx={{ color: '#C0C0C0' }}>
                Já tem uma conta?{' '}
                <Link
                  component={RouterLink}
                  to="/login"
                  sx={{
                    color: '#C0C0C0',
                    textDecoration: 'underline',
                    fontWeight: 'bold',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Faça login
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
    </>
  );
};

export default RegisterPayment; 