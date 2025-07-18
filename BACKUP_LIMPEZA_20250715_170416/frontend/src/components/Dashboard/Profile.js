import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-toastify';

const Profile = ({ open, onClose }) => {
  const { user, updateProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [showApiSecret, setShowApiSecret] = useState(false);
  const [showPassphrase, setShowPassphrase] = useState(false);

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    bitget_api_key: '',
    bitget_api_secret: '',
    bitget_passphrase: ''
  });

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        email: user.email || '',
        bitget_api_key: user.bitget_api_key || '',
        bitget_api_secret: user.bitget_api_secret || '',
        bitget_passphrase: user.bitget_passphrase || ''
      });
    }
  }, [user, open]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    // Só envia as credenciais se alguma delas foi alterada
    const credentialsChanged = (
      formData.bitget_api_key !== user.bitget_api_key ||
      formData.bitget_api_secret !== user.bitget_api_secret ||
      formData.bitget_passphrase !== user.bitget_passphrase
    );

    const dataToSend = {
      full_name: formData.full_name,
      ...(credentialsChanged && {
        bitget_api_key: formData.bitget_api_key,
        bitget_api_secret: formData.bitget_api_secret,
        bitget_passphrase: formData.bitget_passphrase
      })
    };

    try {
      await updateProfile(dataToSend);
      toast.success('Perfil atualizado com sucesso!');
      onClose();
    } catch (error) {
      setError(error.message || 'Erro ao atualizar perfil');
      toast.error(error.message || 'Erro ao atualizar perfil');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Perfil do Usuário {user?.id && `#${user.id}`}
      </DialogTitle>

      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {user?.id && (
              <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  <strong>ID do Usuário:</strong> #{user.id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Status:</strong> {user.is_admin ? 'Administrador' : 'Usuário'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>API Status:</strong> {user.api_configured ? 'Configurada' : 'Não Configurada'}
                </Typography>
              </Box>
            )}

            <TextField
              label="Nome Completo"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              fullWidth
              required
            />

            <TextField
              label="Email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              fullWidth
              required
              type="email"
              disabled
            />

            <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2 }}>
              Credenciais da API Bitget
            </Typography>

            <Alert severity="info" sx={{ mb: 2 }}>
              Suas credenciais da API são salvas de forma segura. Você só precisa inseri-las novamente se desejar alterá-las.
            </Alert>

            <TextField
              label="API Key"
              name="bitget_api_key"
              value={formData.bitget_api_key}
              onChange={handleChange}
              fullWidth
              type={showApiKey ? 'text' : 'password'}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowApiKey(!showApiKey)}
                      edge="end"
                    >
                      {showApiKey ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              label="API Secret"
              name="bitget_api_secret"
              value={formData.bitget_api_secret}
              onChange={handleChange}
              fullWidth
              type={showApiSecret ? 'text' : 'password'}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowApiSecret(!showApiSecret)}
                      edge="end"
                    >
                      {showApiSecret ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              label="Passphrase"
              name="bitget_passphrase"
              value={formData.bitget_passphrase}
              onChange={handleChange}
              fullWidth
              type={showPassphrase ? 'text' : 'password'}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassphrase(!showPassphrase)}
                      edge="end"
                    >
                      {showPassphrase ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            startIcon={loading && <CircularProgress size={20} />}
          >
            Salvar
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default Profile;