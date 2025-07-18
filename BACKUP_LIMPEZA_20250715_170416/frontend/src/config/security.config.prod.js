// 🔒 Configurações de Segurança - PRODUÇÃO
// Nautilus Automação - Security Configuration

const SECURITY_CONFIG = {
  // Content Security Policy otimizado para produção
  CSP: {
    DIRECTIVES: {
      'default-src': ["'self'"],
      'script-src': ["'self'"],
      'style-src': ["'self'", "'unsafe-inline'"],
      'img-src': ["'self'", "data:", "https:"],
      'connect-src': [
        "'self'",
        "https://bigwhale-backend.onrender.com",
        "https://bwhale.site",
        // Domínios de software de segurança
        "https://*.kaspersky-labs.com",
        "https://*.avast.com",
        "https://*.avg.com",
        "https://*.norton.com",
        "https://*.mcafee.com",
        "https://*.bitdefender.com",
        "https://*.eset.com"
      ],
      'font-src': ["'self'"],
      'object-src': ["'none'"],
      'media-src': ["'self'"],
      'frame-src': ["'none'"],
      'base-uri': ["'self'"],
      'form-action': ["'self'"]
    }
  },

  // Configurações de sessão para produção
  SESSION: {
    TIMEOUT: 30 * 60 * 1000, // 30 minutos
    CHECK_INTERVAL: 60 * 1000, // 1 minuto
    WARNING_TIME: 5 * 60 * 1000, // 5 minutos antes de expirar
    SECURE_COOKIES: true,
    SAME_SITE: 'strict'
  },

  // Configurações de logging para produção
  LOGGING: {
    LEVEL: 'error', // Apenas erros em produção
    CONSOLE_ENABLED: false, // Desabilitar console em produção
    REMOTE_LOGGING: true, // Habilitar logging remoto
    SANITIZE_DATA: true, // Sempre sanitizar dados
    MAX_LOG_SIZE: 1000 // Máximo de logs em memória
  },

  // Headers de segurança
  HEADERS: {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
  },

  // Configurações de API
  API: {
    BASE_URL: 'https://bigwhale-backend.onrender.com/api',
    TIMEOUT: 10000, // 10 segundos
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000 // 1 segundo
  },

  // Configurações de performance
  PERFORMANCE: {
    LAZY_LOADING: true,
    CODE_SPLITTING: true,
    COMPRESSION: true,
    CACHE_STRATEGY: 'aggressive'
  },

  // Configurações de monitoramento
  MONITORING: {
    ERROR_REPORTING: true,
    PERFORMANCE_TRACKING: true,
    USER_ANALYTICS: false, // Desabilitado por privacidade
    HEALTH_CHECK_INTERVAL: 5 * 60 * 1000 // 5 minutos
  }
};

// Validação de configuração
if (typeof window !== 'undefined') {
  // Verificar se estamos em produção
  const isProduction = process.env.NODE_ENV === 'production';
  
  if (isProduction) {
    // Desabilitar ferramentas de desenvolvimento
    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
      window.__REACT_DEVTOOLS_GLOBAL_HOOK__.onCommitFiberRoot = null;
      window.__REACT_DEVTOOLS_GLOBAL_HOOK__.onCommitFiberUnmount = null;
    }
    
    // Desabilitar console em produção (exceto erros)
    const originalConsole = { ...console };
    console.log = () => {};
    console.debug = () => {};
    console.info = () => {};
    console.warn = originalConsole.warn;
    console.error = originalConsole.error;
  }
}

export default SECURITY_CONFIG;
