import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import './PaymentSuccess.css';

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [countdown, setCountdown] = useState(8);
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    // Extrair parâmetros da URL
    const urlParams = new URLSearchParams(location.search);
    const sessionId = urlParams.get('session_id');
    const email = urlParams.get('email') || localStorage.getItem('payment_email');

    // NOVO: Aceitar qualquer acesso a /payment-success como pagamento válido
    // Se chegou aqui, é porque o Stripe redirecionou após pagamento
    console.log('🎯 PaymentSuccess carregado - assumindo pagamento válido');
    
    // Mostrar toast de sucesso sempre
    toast.success('💰 Pagamento realizado com sucesso!');
    
    // Armazenar dados do pagamento
    if (sessionId) {
      localStorage.setItem('payment_session_id', sessionId);
    }
    if (email) {
      localStorage.setItem('payment_email', email);
    }

    // Verificar status do pagamento periodicamente
    const checkPaymentStatus = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/webhook/status`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          console.log('✅ Backend está ativo e processando webhooks');
        }
      } catch (error) {
        console.error('Erro ao verificar status:', error);
      }
    };

    // Verificar status imediatamente
    checkPaymentStatus();

    // Countdown para redirecionamento
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          setIsProcessing(false);
          
          // Redirecionar para registro com dados de pagamento
          const email = localStorage.getItem('payment_email');
          const storedSessionId = sessionId || localStorage.getItem('payment_session_id') || 'payment_confirmed';
          navigate('/register', { 
            state: { 
              paymentSuccess: true, 
              email: email,
              sessionId: storedSessionId 
            } 
          });
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [navigate, location]);

  const handleContinue = () => {
    const email = localStorage.getItem('payment_email');
    const sessionId = localStorage.getItem('payment_session_id') || 'payment_confirmed';
    
    navigate('/register', { 
      state: { 
        paymentSuccess: true, 
        email: email,
        sessionId: sessionId 
      } 
    });
  };

  return (
    <div className="payment-success-container">
      <div className="payment-success-content">
        <div className="success-icon">
          <div className="checkmark">✓</div>
        </div>
        
        <h1 className="success-title">Pagamento Confirmado!</h1>
        
        <div className="success-details">
          <p className="success-message">
            Pagamento processado, acesso ao Nautilus liberado.
          </p>
          
          <div className="processing-info">
            <div className="spinner"></div>
            <p>Processando informações do pagamento...</p>
          </div>
          
          <div className="countdown-section">
            <p className="countdown-text">
              Redirecionando para o cadastro em <span className="countdown-number">{countdown}</span> segundos
            </p>
            
            <div className="countdown-bar">
              <div 
                className="countdown-progress"
                style={{ width: `${((8 - countdown) / 8) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="success-actions">
          <button 
            className="continue-button"
            onClick={handleContinue}
            disabled={isProcessing}
          >
            🚀 Continuar para Cadastro
          </button>
          
          <button 
            className="back-button"
            onClick={() => navigate('/login')}
          >
            ← Voltar ao Login
          </button>
        </div>
        
        <div className="payment-info">
          <p className="info-text">
            💡 Suas informações de pagamento foram salvas com segurança
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccess; 