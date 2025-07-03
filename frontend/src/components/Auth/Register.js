// frontend/src/components/Auth/Register.js
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
  ListItemText
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Person,
  Check,
  Close,
  VpnKey,
  Api
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import authService from '../../services/authService';
import logger from '../../utils/logger';
import FinanceBackground from './FinanceBackground';

const Register = () => {
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
  


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (name === 'password') {
      validatePassword(value);
    }

    // Limpar erro quando usuário começar a digitar
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
    const requiredFields = [full_name, email, password, confirmPassword, bitget_api_key, bitget_api_secret, bitget_passphrase];
    if (requiredFields.some(field => !field)) {
      setError('Todos os campos são obrigatórios');
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
      };

      logger.secure('Iniciando processo de registro');
      const response = await authService.register(registrationData);
      logger.secure('Registro processado com sucesso');
      
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
      logger.error('Erro no registro:', error);
      
      if (error.response?.status === 409) {
        setError('Este email já está registrado. Tente fazer login ou use outro email.');
      } else if (error.response?.status === 400) {
        const errorMsg = error.response.data?.message || 'Dados inválidos fornecidos';
        if (errorMsg.includes('API')) {
          setError(`Erro nas credenciais da Bitget: ${errorMsg}`);
        } else {
          setError(errorMsg);
        }
      } else if (error.response?.status === 422) {
        setError('Erro de validação: Verifique se todos os campos estão preenchidos corretamente.');
      } else if (error.response?.status >= 500) {
        setError('Erro interno do servidor. Tente novamente em alguns minutos.');
      } else {
        setError(error.response?.data?.message || 'Erro ao criar conta. Tente novamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  const ValidationIcon = ({ isValid }) => (
    isValid ? (
      <Check sx={{ color: 'green', fontSize: 16 }} />
    ) : (
      <Close sx={{ color: 'red', fontSize: 16 }} />
    )
  );

  return (
    <>
      <Container maxWidth="md">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            py: 4
          }}
        >
        <Paper
          elevation={8}
          sx={{
            p: 4,
            width: '100%',
            maxWidth: 600,
            background: 'rgba(0, 0, 0, 0.7)',
            border: '1px solid rgba(192, 192, 192, 0.3)',
            borderRadius: 2
          }}
        >
          {/* Logo/Título */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography
              variant="h4"
              component="h1"
              sx={{
                fontWeight: 'bold',
                color: '#C0C0C0',
                mb: 1
              }}
            >
              Nautilus Automação
            </Typography>
            <Typography
              variant="subtitle1"
              sx={{ color: '#C0C0C0', mb: 2 }}
            >
              Crie sua conta de trading
            </Typography>
          </Box>

          {/* Formulário Principal */}
          <Box component="form" onSubmit={handleSubmit}>
            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: 3,
                  backgroundColor: 'rgba(211, 47, 47, 0.15)',
                  color: '#ff6b6b',
                  border: '2px solid rgba(211, 47, 47, 0.5)',
                  borderRadius: 2
                }}
                onClose={() => setError('')}
              >
                {error}
              </Alert>
            )}

            {/* Mostrar o restante do formulário apenas se tiver acesso válido */}
            <>
              {/* Nome Completo */}
              <TextField
                fullWidth
                name="full_name"
                label="Nome Completo"
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

              {/* Email */}
              <TextField
                fullWidth
                name="email"
                label="Email"
                type="email"
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

              {/* Senha */}
              <TextField
                fullWidth
                name="password"
                label="Senha"
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

              {/* Validação da senha */}
              {formData.password && (
                <Box sx={{ mt: 1, mb: 2 }}>
                  <Typography variant="caption" sx={{ color: '#C0C0C0', mb: 1, display: 'block' }}>
                    Requisitos da senha:
                  </Typography>
                  <List dense sx={{ py: 0 }}>
                    <ListItem sx={{ py: 0, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <ValidationIcon isValid={passwordValidation.length} />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Pelo menos 8 caracteres" 
                        primaryTypographyProps={{ variant: 'caption', sx: { color: '#C0C0C0' } }}
                      />
                    </ListItem>
                    <ListItem sx={{ py: 0, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <ValidationIcon isValid={passwordValidation.uppercase} />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Uma letra maiúscula" 
                        primaryTypographyProps={{ variant: 'caption', sx: { color: '#C0C0C0' } }}
                      />
                    </ListItem>
                    <ListItem sx={{ py: 0, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <ValidationIcon isValid={passwordValidation.lowercase} />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Uma letra minúscula" 
                        primaryTypographyProps={{ variant: 'caption', sx: { color: '#C0C0C0' } }}
                      />
                    </ListItem>
                    <ListItem sx={{ py: 0, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <ValidationIcon isValid={passwordValidation.number} />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Um número" 
                        primaryTypographyProps={{ variant: 'caption', sx: { color: '#C0C0C0' } }}
                      />
                    </ListItem>
                    <ListItem sx={{ py: 0, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <ValidationIcon isValid={passwordValidation.special} />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Um caractere especial (@$!%*?&_-)" 
                        primaryTypographyProps={{ variant: 'caption', sx: { color: '#C0C0C0' } }}
                      />
                    </ListItem>
                  </List>
                </Box>
              )}

              {/* Confirmar Senha */}
              <TextField
                fullWidth
                name="confirmPassword"
                label="Confirmar Senha"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleChange}
                margin="normal"
                required
                error={!!(formData.confirmPassword && formData.password !== formData.confirmPassword)}
                helperText={
                  formData.confirmPassword && formData.password !== formData.confirmPassword
                    ? 'As senhas não coincidem'
                    : ''
                }
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

              {/* API Key da Bitget */}
              <TextField
                fullWidth
                name="bitget_api_key"
                label="Bitget API Key"
                value={formData.bitget_api_key}
                onChange={handleChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <VpnKey sx={{ color: '#C0C0C0' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <Tooltip title="Sua chave de API da Bitget para acessar dados de trading">
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

              {/* API Secret da Bitget */}
              <TextField
                fullWidth
                name="bitget_api_secret"
                label="Bitget API Secret"
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

              {/* Passphrase da Bitget */}
              <TextField
                fullWidth
                name="bitget_passphrase"
                label="Bitget Passphrase"
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

              {/* Aviso de segurança */}
              <Alert severity="info" sx={{ mt: 2, mb: 2, backgroundColor: 'rgba(0, 0, 0, 0.6)', color: '#C0C0C0', border: '1px solid rgba(192, 192, 192, 0.3)' }}>
                <Typography variant="caption" sx={{ color: '#C0C0C0' }}>
                  🔒 Suas credenciais da API são criptografadas com AES-256 e armazenadas com segurança.
                  Nunca compartilhe suas chaves de API com terceiros.
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

export default Register;

