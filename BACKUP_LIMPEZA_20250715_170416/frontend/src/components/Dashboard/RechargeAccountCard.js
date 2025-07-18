// frontend/src/components/Dashboard/RechargeAccountCard.js
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  InputAdornment,
  Chip,
  useTheme,
  IconButton,
  Grid
} from '@mui/material';
import {
  AccountBalanceWallet,
  Add,
  AttachMoney,
  CreditCard
} from '@mui/icons-material';
import { toast } from 'react-toastify';

const RechargeAccountCard = () => {
  const theme = useTheme();
  const [openDialog, setOpenDialog] = useState(false);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Valores sugeridos para recarga
  const suggestedAmounts = [
    { value: 9, url: 'https://pay.hub.la/ekfJp2uXQ0S5ZBb65Otb' },
    { value: 50, url: 'https://pay.hub.la/MdORdaFcTzWvhT9IkZHP' },
    { value: 100, url: 'https://pay.hub.la/mFfwQbUAqILTw8bfDXjo' },
    { value: 200, url: 'https://pay.hub.la/EVrxnuDyf4JeB0uIYaFC' },
    { value: 500, url: 'https://pay.hub.la/LmFhy6R6HP3fjoJxZe5z' }
  ];

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setRechargeAmount('');
  };

  const handleAmountSelect = (amount) => {
    setRechargeAmount(amount.value.toString());
  };

  const handleRecharge = async () => {
    if (!rechargeAmount || parseFloat(rechargeAmount) <= 0) {
      toast.error('Por favor, insira um valor válido para recarga');
      return;
    }

    // Verificar se é um valor sugerido
    const suggestedAmount = suggestedAmounts.find(amount => amount.value === parseFloat(rechargeAmount));
    
    if (suggestedAmount) {
      // Redirecionar para o link de pagamento
      window.open(suggestedAmount.url, '_blank');
      handleCloseDialog();
    } else {
      // Para valores customizados, mostrar mensagem informativa
      toast.error('Para valores personalizados, entre em contato com o suporte.');
    }
  };

  return (
    <>
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)'
          }
        }}
        onClick={handleOpenDialog}
      >
        <CardContent sx={{ 
          p: 1.5, 
          '&:last-child': { pb: 1.5 },
          minHeight: '180px',
          maxHeight: '180px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            mb: 0.5
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <AccountBalanceWallet sx={{ fontSize: 32, opacity: 0.9 }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Recarregar Conta
              </Typography>
            </Box>
            <Add sx={{ fontSize: 24, opacity: 0.8 }} />
          </Box>
          
          <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5, fontSize: '0.875rem' }}>
            Adicione fundos à sua conta para cobrir comissões e taxas de trading
          </Typography>
          
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1
          }}>
            <CreditCard sx={{ fontSize: 18, opacity: 0.8 }} />
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Clique para recarregar
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Dialog de Recarga */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ 
          textAlign: 'center',
          pb: 1,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <AccountBalanceWallet />
            <Typography variant="h6">Recarregar Conta</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ pt: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
            Selecione ou digite o valor que deseja adicionar à sua conta
          </Typography>
          
          {/* Valores Sugeridos */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold' }}>
              Valores Sugeridos:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {suggestedAmounts.map((amount) => (
                <Chip
                  key={amount.value}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      ${amount.value}
                      {amount.value === 9 && (
                        <Chip 
                          label="TESTE" 
                          size="small" 
                          sx={{ 
                            backgroundColor: '#ff9800', 
                            color: 'white',
                            fontSize: '8px',
                            height: '16px',
                            ml: 0.5
                          }} 
                        />
                      )}
                    </Box>
                  }
                  onClick={() => handleAmountSelect(amount)}
                  color={rechargeAmount === amount.value.toString() ? 'primary' : 'default'}
                  variant={rechargeAmount === amount.value.toString() ? 'filled' : 'outlined'}
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: theme.palette.primary.light,
                      color: 'white'
                    }
                  }}
                />
              ))}
            </Box>
          </Box>
          
          {/* Campo de Valor Personalizado */}
          <TextField
            fullWidth
            label="Valor da Recarga"
            type="number"
            value={rechargeAmount}
            onChange={(e) => setRechargeAmount(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <AttachMoney />
                </InputAdornment>
              ),
            }}
            placeholder="Digite o valor desejado"
            helperText="Valor mínimo: $10.00"
            sx={{ mb: 2 }}
          />
          
          {/* Informações Adicionais */}
          <Box sx={{ 
            p: 2, 
            bgcolor: 'background.default', 
            borderRadius: 1,
            border: `1px solid ${theme.palette.divider}`
          }}>
            <Typography variant="body2" color="text.secondary">
              💡 <strong>Informação:</strong> Os fundos adicionados serão utilizados automaticamente 
              para cobrir comissões de trading e outras taxas da plataforma.
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ p: 3, pt: 2 }}>
          <Button 
            onClick={handleCloseDialog}
            variant="outlined"
            sx={{ minWidth: 100 }}
          >
            Cancelar
          </Button>
          <Button 
            onClick={handleRecharge}
            variant="contained"
            disabled={!rechargeAmount || parseFloat(rechargeAmount) < 10 || loading}
            sx={{ 
              minWidth: 120,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            {loading ? 'Processando...' : 'Recarregar'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default RechargeAccountCard;