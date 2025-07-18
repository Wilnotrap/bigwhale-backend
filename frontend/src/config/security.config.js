/**
 * Configurações de Segurança Centralizadas
 * Todas as configurações de segurança da aplicação
 */

export const SECURITY_CONFIG = {
  // Configurações de logging
  LOGGING: {
    // Palavras-chave que nunca devem aparecer nos logs
    SENSITIVE_KEYWORDS: [
      'password', 'senha', 'token', 'api_key', 'apikey', 'secret', 'credential',
      'balance', 'saldo', 'profit', 'lucro', 'loss', 'prejuizo', 'pnl',
      'email', 'phone', 'telefone', 'cpf', 'cnpj', 'user_id', 'private_key',
      'access_token', 'refresh_token', 'session_id', 'auth_token'
    ],
    
    // Níveis de log permitidos por ambiente
    ALLOWED_LEVELS: {
      development: ['info', 'warn', 'error', 'debug', 'secure', 'audit'],
      production: ['error', 'warn'], // Apenas erros e avisos em produção
      test: ['error']
    }
  },

  // Configurações de sessão
  SESSION: {
    TIMEOUT_MINUTES: 30, // Timeout de inatividade
    MAX_CONCURRENT_SESSIONS: 3, // Máximo de sessões simultâneas
    SECURE_STORAGE_KEYS: [
      'api_key', 'token', 'user_data', 'credentials', 'balance',
      'private_key', 'session_token', 'refresh_token'
    ]
  },

  // Configurações de CSP (Content Security Policy)
  CSP: {
    DIRECTIVES: {
      'default-src': ["'self'"],
      'script-src': ["'self'", "'unsafe-inline'"], // unsafe-inline necessário para React
      'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
      'img-src': ["'self'", 'data:', 'https:'],
      'connect-src': [
        "'self'", 
        'ws://localhost:3000',
        'https://bigwhale-backend.onrender.com',

      ],
      'font-src': ["'self'", 'https://fonts.gstatic.com'],
      'object-src': ["'none'"],
      'media-src': ["'self'"],
      'frame-src': ["'self'"],
      'base-uri': ["'self'"],
      'form-action': ["'self'"]
    }
  },

  // URLs e origens permitidas
  ALLOWED_ORIGINS: {
    development: [
      'http://localhost:3000',
      'http://127.0.0.1:3000'
    ],
    production: [
      'https://bwhale.site',
      'https://bigwhale-backend.onrender.com'
    ]
  },

  // Configurações de API
  API: {
    // Headers obrigatórios para requisições
    REQUIRED_HEADERS: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    
    // Timeout para requisições (ms)
    REQUEST_TIMEOUT: 30000,
    
    // Rate limiting (requisições por minuto)
    RATE_LIMIT: {
      MAX_REQUESTS_PER_MINUTE: 60,
      BURST_LIMIT: 10
    }
  },

  // Configurações de validação
  VALIDATION: {
    // Padrões para validação de entrada
    PATTERNS: {
      EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      PHONE: /^\+?[1-9]\d{1,14}$/,
      API_KEY: /^[A-Za-z0-9+/=]{20,}$/,
      TOKEN: /^[A-Za-z0-9._-]+$/
    },
    
    // Tamanhos máximos
    MAX_LENGTHS: {
      EMAIL: 254,
      PASSWORD: 128,
      NAME: 100,
      MESSAGE: 1000
    }
  },

  // Configurações de monitoramento
  MONITORING: {
    // Eventos que devem ser auditados
    AUDIT_EVENTS: [
      'login_attempt',
      'login_success',
      'login_failure',
      'logout',
      'api_key_access',
      'balance_view',
      'trade_execution',
      'admin_access',
      'devtools_detected',
      'suspicious_activity'
    ],
    
    // Limites para detecção de atividade suspeita
    SUSPICIOUS_ACTIVITY: {
      MAX_FAILED_LOGINS: 5,
      MAX_API_CALLS_PER_MINUTE: 100,
      MAX_CONCURRENT_REQUESTS: 10
    }
  },

  // Configurações de desenvolvimento
  DEVELOPMENT: {
    // Avisos que devem ser exibidos em desenvolvimento
    WARNINGS: {
      SHOW_SECURITY_WARNINGS: true,
      SHOW_PERFORMANCE_WARNINGS: true,
      SHOW_DEPRECATION_WARNINGS: true
    },
    
    // Ferramentas de debug permitidas
    DEBUG_TOOLS: {
      ALLOW_CONSOLE_LOGS: true,
      ALLOW_REACT_DEVTOOLS: true,
      ALLOW_REDUX_DEVTOOLS: true
    }
  },

  // Configurações de produção
  PRODUCTION: {
    // Recursos desabilitados em produção
    DISABLED_FEATURES: {
      CONSOLE_LOGS: true,
      DEBUG_MODE: true,
      SOURCE_MAPS: true,
      ERROR_OVERLAY: true
    },
    
    // Monitoramento adicional em produção
    ENHANCED_MONITORING: {
      TRACK_USER_INTERACTIONS: true,
      MONITOR_PERFORMANCE: true,
      DETECT_DEVTOOLS: true,
      LOG_SECURITY_EVENTS: true
    }
  },

  // Mensagens de segurança
  MESSAGES: {
    UNAUTHORIZED_ACCESS: 'Acesso não autorizado detectado. Todas as atividades são monitoradas.',
    SESSION_EXPIRED: 'Sua sessão expirou por motivos de segurança. Faça login novamente.',
    SUSPICIOUS_ACTIVITY: 'Atividade suspeita detectada. Contate o administrador se necessário.',
    DEVTOOLS_WARNING: 'Ferramentas de desenvolvedor detectadas. Dados sensíveis foram protegidos.',
    SECURITY_VIOLATION: 'Violação de segurança detectada. Ação bloqueada.'
  }
};

// Função para obter configuração baseada no ambiente
export const getSecurityConfig = (environment = process.env.NODE_ENV) => {
  const config = { ...SECURITY_CONFIG };
  
  // Aplica configurações específicas do ambiente
  if (environment === 'production') {
    config.CURRENT_ENVIRONMENT = 'production';
    config.ALLOWED_ORIGINS = config.ALLOWED_ORIGINS.production;
  } else {
    config.CURRENT_ENVIRONMENT = 'development';
    config.ALLOWED_ORIGINS = config.ALLOWED_ORIGINS.development;
  }
  
  return config;
};

// Função para validar configuração de segurança
export const validateSecurityConfig = () => {
  const config = getSecurityConfig();
  const errors = [];
  
  // Verifica se origens permitidas estão definidas
  if (!config.ALLOWED_ORIGINS || config.ALLOWED_ORIGINS.length === 0) {
    errors.push('Nenhuma origem permitida definida');
  }
  
  // Verifica se timeout de sessão está configurado
  if (!config.SESSION.TIMEOUT_MINUTES || config.SESSION.TIMEOUT_MINUTES < 5) {
    errors.push('Timeout de sessão deve ser pelo menos 5 minutos');
  }
  
  // Verifica se palavras-chave sensíveis estão definidas
  if (!config.LOGGING.SENSITIVE_KEYWORDS || config.LOGGING.SENSITIVE_KEYWORDS.length === 0) {
    errors.push('Palavras-chave sensíveis não definidas');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export default SECURITY_CONFIG;