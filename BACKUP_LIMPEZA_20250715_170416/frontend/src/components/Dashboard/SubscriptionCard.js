// frontend/src/components/Dashboard/SubscriptionCard.js
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  useTheme
} from '@mui/material';
import {
  Subscriptions,
  Star,
  Close
} from '@mui/icons-material';

const SubscriptionCard = () => {
  const theme = useTheme();
  const [openDialog, setOpenDialog] = useState(false);

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handlePaymentClick = (link) => {
    window.open(link, '_blank', 'noopener,noreferrer');
  };

  return (
    <>
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)',
          color: 'white',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 8px 25px rgba(255, 107, 107, 0.3)'
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
              <Subscriptions sx={{ fontSize: 32, opacity: 0.9 }} />
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Assinatura / Renovação
              </Typography>
            </Box>
            <Star sx={{ fontSize: 24, opacity: 0.8 }} />
          </Box>
          
          <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5, fontSize: '0.875rem' }}>
            Gerencie sua assinatura e acesse recursos premium da plataforma
          </Typography>
          
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1
          }}>
            <Star sx={{ fontSize: 18, opacity: 0.8 }} />
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Clique para assinar
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Dialog de Assinatura */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: 'hsla(0, 0.00%, 0.00%, 0.93) !important',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(102, 255, 204, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
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
          <IconButton onClick={handleCloseDialog} sx={{ color: 'white' }}>
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
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mt: 2, fontStyle: 'italic' }}>
            (Modo sem cobrança de comissão)
          </Typography>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default SubscriptionCard;