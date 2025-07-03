// Sistema de logs seguros - apenas em desenvolvimento
const isDevelopment = process.env.NODE_ENV === 'development';
const isProduction = process.env.NODE_ENV === 'production';

// Lista de palavras-chave sensíveis que nunca devem ser logadas
const SENSITIVE_KEYWORDS = [
  'password', 'senha', 'token', 'api_key', 'apikey', 'secret', 'credential',
  'balance', 'saldo', 'profit', 'lucro', 'loss', 'prejuizo', 'pnl',
  'email', 'phone', 'telefone', 'cpf', 'cnpj', 'user_id'
];

// Função para sanitizar dados sensíveis
function sanitizeData(data) {
  if (typeof data === 'string') {
    const lowerData = data.toLowerCase();
    const hasSensitiveData = SENSITIVE_KEYWORDS.some(keyword => 
      lowerData.includes(keyword.toLowerCase())
    );
    return hasSensitiveData ? '[DADOS SENSÍVEIS OCULTADOS]' : data;
  }
  
  if (typeof data === 'object' && data !== null) {
    const sanitized = {};
    for (const [key, value] of Object.entries(data)) {
      const lowerKey = key.toLowerCase();
      const hasSensitiveKey = SENSITIVE_KEYWORDS.some(keyword => 
        lowerKey.includes(keyword.toLowerCase())
      );
      
      if (hasSensitiveKey) {
        sanitized[key] = '[OCULTADO]';
      } else {
        sanitized[key] = sanitizeData(value);
      }
    }
    return sanitized;
  }
  
  return data;
}

// Sistema de logger seguro
const logger = {
  // Log de informação - apenas em desenvolvimento
  info: (message, ...args) => {
    if (isDevelopment) {
      const sanitizedArgs = args.map(sanitizeData);
      console.log(`[INFO] ${message}`, ...sanitizedArgs);
    }
  },
  
  // Log de erro - sanitizado mesmo em desenvolvimento
  error: (message, error) => {
    if (isDevelopment) {
      const errorMessage = error?.message || error;
      const sanitizedError = sanitizeData(errorMessage);
      console.error(`[ERROR] ${message}`, sanitizedError);
    }
    // Em produção, apenas envia para serviço de monitoramento (se configurado)
    if (isProduction && window.errorReporting) {
      window.errorReporting.captureException(new Error(`${message}: ${error?.message || error}`));
    }
  },
  
  // Log de debug - NUNCA em produção
  debug: (message, ...args) => {
    if (isDevelopment) {
      const sanitizedArgs = args.map(sanitizeData);
      console.log(`[DEBUG] ${message}`, ...sanitizedArgs);
    }
  },
  
  // Log seguro para operações sensíveis - apenas status
  secure: (operation, status = 'OK', details = null) => {
    if (isDevelopment) {
      const safeDetails = details ? '[DETALHES OCULTADOS POR SEGURANÇA]' : '';
      console.log(`[SECURE] ${operation} - Status: ${status} ${safeDetails}`);
    }
  },
  
  // Log de warning - sanitizado
  warn: (message, ...args) => {
    if (isDevelopment) {
      const sanitizedArgs = args.map(sanitizeData);
      console.warn(`[WARN] ${message}`, ...sanitizedArgs);
    }
  },
  
  // Log para auditoria - apenas em desenvolvimento
  audit: (action, userId = null, details = null) => {
    if (isDevelopment) {
      const safeUserId = userId ? '[USER_ID_OCULTADO]' : 'N/A';
      const safeDetails = details ? '[DETALHES_OCULTADOS]' : 'N/A';
      console.log(`[AUDIT] Ação: ${action} | Usuário: ${safeUserId} | Detalhes: ${safeDetails}`);
    }
  },
  
  // Método para verificar se dados são sensíveis
  isSensitive: (data) => {
    if (typeof data === 'string') {
      const lowerData = data.toLowerCase();
      return SENSITIVE_KEYWORDS.some(keyword => 
        lowerData.includes(keyword.toLowerCase())
      );
    }
    return false;
  }
};

// Sobrescrever console.log em produção para prevenir vazamentos
if (isProduction) {
  const originalConsole = { ...console };
  
  console.log = () => {}; // Desabilita completamente
  console.debug = () => {}; // Desabilita completamente
  console.trace = () => {}; // Desabilita completamente
  console.table = () => {}; // Desabilita completamente
  
  // Manter apenas error e warn com sanitização
  console.error = (message, ...args) => {
    const sanitizedArgs = args.map(arg => sanitizeData(arg));
    originalConsole.error(message, ...sanitizedArgs);
  };
  
  console.warn = (message, ...args) => {
    const sanitizedArgs = args.map(arg => sanitizeData(arg));
    originalConsole.warn(message, ...sanitizedArgs);
  };
}

export default logger;