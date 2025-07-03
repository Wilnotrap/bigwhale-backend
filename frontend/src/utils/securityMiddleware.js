/**
 * Middleware de Segurança para Frontend
 * Protege contra XSS, CSRF, e outras vulnerabilidades
 */

import logger from './logger';
import { SECURITY_CONFIG } from '../config/security.config';

class SecurityMiddleware {
  constructor() {
    this.initializeSecurityHeaders();
    this.setupXSSProtection();
    this.setupCSRFProtection();
    this.monitorConsoleAccess();
  }

  // Configura headers de segurança
  initializeSecurityHeaders() {
    // Content Security Policy baseado na configuração
    const cspDirectives = SECURITY_CONFIG.CSP.DIRECTIVES;
    
    // Garantir que o backend está incluído no connect-src
    if (cspDirectives['connect-src'] && !cspDirectives['connect-src'].includes('https://bigwhale-backend.onrender.com')) {
      cspDirectives['connect-src'].push('https://bigwhale-backend.onrender.com');
    }
    
    const csp = Object.entries(cspDirectives)
      .map(([directive, sources]) => `${directive} ${sources.join(' ')}`)
      .join('; ');

    // Remove CSP existente se houver
    const existingCSP = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
    if (existingCSP) {
      existingCSP.remove();
    }
    
    // Aplica novo CSP
    const meta = document.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    meta.content = csp;
    document.head.appendChild(meta);
    logger.secure('CSP aplicado via JavaScript - Status: OK');
    console.log('CSP aplicado:', csp);
  }

  // Proteção contra XSS
  setupXSSProtection() {
    // Sanitiza dados antes de inserir no DOM
    this.sanitizeHTML = (html) => {
      const div = document.createElement('div');
      div.textContent = html;
      return div.innerHTML;
    };

    // Monitora tentativas de injeção de script
    const originalInnerHTML = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML') || 
                             Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'innerHTML');
    
    if (originalInnerHTML && originalInnerHTML.set) {
      Object.defineProperty(Element.prototype, 'innerHTML', {
        get: originalInnerHTML.get,
        set: function(value) {
          if (typeof value === 'string' && /<script[^>]*>.*?<\/script>/gi.test(value)) {
            logger.error('Tentativa de injeção XSS bloqueada', { element: this.tagName });
            return;
          }
          return originalInnerHTML.set.call(this, value);
        },
        configurable: true,
        enumerable: true
      });
    }

    logger.secure('Proteção XSS ativada');
  }

  // Proteção contra CSRF
  setupCSRFProtection() {
    // Gera token CSRF para requisições
    this.generateCSRFToken = () => {
      const array = new Uint8Array(32);
      crypto.getRandomValues(array);
      return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    };

    // Armazena token CSRF no sessionStorage (mais seguro que localStorage)
    if (!sessionStorage.getItem('csrf_token')) {
      const token = this.generateCSRFToken();
      sessionStorage.setItem('csrf_token', token);
      logger.secure('Token CSRF gerado');
    }

    // Intercepta requisições para adicionar token CSRF
    this.addCSRFToRequests();
  }

  // Adiciona token CSRF às requisições
  addCSRFToRequests() {
    // Intercepta fetch
    const originalFetch = window.fetch.bind(window);
    window.fetch = function(url, options = {}) {
      const token = sessionStorage.getItem('csrf_token');
      if (token && options.method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method.toUpperCase())) {
        options.headers = {
          ...options.headers,
          'X-CSRF-Token': token
        };
      }
      return originalFetch(url, options);
    };

    logger.secure('Interceptador CSRF configurado');
  }

  // Monitora acesso ao console em produção
  monitorConsoleAccess() {
    if (process.env.NODE_ENV === 'production') {
      // Detecta abertura do DevTools
      let devtools = {
        open: false,
        orientation: null
      };

      const threshold = 160;
      setInterval(() => {
        if (window.outerHeight - window.innerHeight > threshold || 
            window.outerWidth - window.innerWidth > threshold) {
          if (!devtools.open) {
            devtools.open = true;
            this.handleDevToolsOpen();
          }
        } else {
          devtools.open = false;
        }
      }, 500);

      // Detecta tentativas de debug
      const originalDebugger = window.debugger;
      Object.defineProperty(window, 'debugger', {
        get: () => {
          this.handleDebugAttempt();
          return originalDebugger;
        }
      });
    }
  }

  // Manipula abertura do DevTools
  handleDevToolsOpen() {
    logger.audit('DevTools detectado em produção');
    
    // Limpa dados sensíveis do sessionStorage/localStorage
    const sensitiveKeys = ['api_key', 'token', 'user_data', 'balance'];
    sensitiveKeys.forEach(key => {
      sessionStorage.removeItem(key);
      localStorage.removeItem(key);
    });

    // Exibe aviso
    if (window.confirm('Ferramentas de desenvolvedor detectadas. Por segurança, alguns dados foram limpos. Deseja continuar?')) {
      logger.audit('Usuário confirmou uso do DevTools');
    } else {
      window.location.reload();
    }
  }

  // Manipula tentativas de debug
  handleDebugAttempt() {
    logger.audit('Tentativa de debug detectada');
    console.clear();
  }

  // Valida origem das requisições
  validateRequestOrigin(url) {
    const allowedOrigins = [
      'http://localhost:3000',
      'http://localhost:5000',
      window.location.origin
    ];

    try {
      const requestOrigin = new URL(url).origin;
      return allowedOrigins.includes(requestOrigin);
    } catch {
      return false;
    }
  }

  // Sanitiza dados de entrada
  sanitizeInput(input) {
    if (typeof input !== 'string') return input;

    // Remove scripts maliciosos
    const scriptPattern = /<script[^>]*>.*?<\/script>/gi;
    const eventPattern = /on\w+\s*=/gi;
    const javascriptPattern = /javascript:/gi;

    return input
      .replace(scriptPattern, '')
      .replace(eventPattern, '')
      .replace(javascriptPattern, '')
      .trim();
  }

  // Valida tokens de API
  validateAPIToken(token) {
    if (!token || typeof token !== 'string') {
      logger.error('Token de API inválido');
      return false;
    }

    // Verifica formato básico do token
    if (token.length < 20 || !/^[A-Za-z0-9+/=]+$/.test(token)) {
      logger.error('Formato de token inválido');
      return false;
    }

    return true;
  }

  // Limpa dados sensíveis da memória
  clearSensitiveData() {
    // Limpa variáveis globais que podem conter dados sensíveis
    const sensitiveGlobals = ['apiKey', 'userToken', 'password', 'balance'];
    sensitiveGlobals.forEach(global => {
      if (window[global]) {
        delete window[global];
      }
    });

    // Limpa storage
    const sensitiveStorageKeys = ['api_key', 'token', 'user_data', 'credentials'];
    sensitiveStorageKeys.forEach(key => {
      sessionStorage.removeItem(key);
      localStorage.removeItem(key);
    });

    logger.secure('Dados sensíveis limpos da memória');
  }

  // Configura timeout de sessão
  setupSessionTimeout(timeoutMinutes = 30) {
    let lastActivity = Date.now();

    // Monitora atividade do usuário
    const updateActivity = () => {
      lastActivity = Date.now();
    };

    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
      document.addEventListener(event, updateActivity, true);
    });

    // Verifica timeout
    setInterval(() => {
      const now = Date.now();
      const timeSinceLastActivity = now - lastActivity;
      const timeoutMs = timeoutMinutes * 60 * 1000;

      if (timeSinceLastActivity > timeoutMs) {
        logger.audit('Sessão expirada por inatividade');
        this.clearSensitiveData();
        
        // Redireciona para login
        if (window.location.pathname !== '/login') {
          window.location.href = '/login?reason=timeout';
        }
      }
    }, 60000); // Verifica a cada minuto

    logger.secure(`Timeout de sessão configurado: ${timeoutMinutes} minutos`);
  }

  // Inicializa todas as proteções
  initialize() {
    logger.secure('Middleware de segurança inicializado');
    this.setupSessionTimeout();
    
    // Limpa dados sensíveis ao sair da página
    window.addEventListener('beforeunload', () => {
      this.clearSensitiveData();
    });

    // Monitora mudanças de visibilidade da página
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        logger.audit('Página ficou oculta');
      }
    });
  }
}

// Instância singleton com inicialização lazy
let securityMiddleware = null;

const getSecurityMiddleware = () => {
  if (!securityMiddleware) {
    securityMiddleware = new SecurityMiddleware();
  }
  return securityMiddleware;
};

export default getSecurityMiddleware;
export { SecurityMiddleware };