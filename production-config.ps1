# ⚙️ Script de Configuração para Produção
# Nautilus Automação - Otimização para Deploy

Write-Host "⚙️ Configuração para Produção - Nautilus Automação" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Yellow

# Configurações
$DOMAIN = Read-Host "Digite seu domínio (ex: seusite.com)"
$FRONTEND_DIR = "./frontend"
$BACKEND_DIR = "./backend"
$CONFIG_DIR = "./frontend/src/config"

Write-Host "🔧 Otimizando configurações para produção..." -ForegroundColor Blue

# 1. ATUALIZAR SECURITY.CONFIG.JS PARA PRODUÇÃO
Write-Host "🔒 Atualizando configurações de segurança..." -ForegroundColor Blue

$securityConfigProd = @"
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
        "https://$DOMAIN",
        "https://$DOMAIN/api",
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
    BASE_URL: 'https://$DOMAIN/api',
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
"@

$securityConfigProd | Out-File -FilePath "$CONFIG_DIR/security.config.prod.js" -Encoding UTF8
Write-Host "✅ Configuração de segurança para produção criada" -ForegroundColor Green

# 2. CRIAR PACKAGE.JSON SCRIPTS OTIMIZADOS
Write-Host "📦 Criando scripts otimizados..." -ForegroundColor Blue

# Ler package.json atual
$packageJsonPath = "$FRONTEND_DIR/package.json"
if (Test-Path $packageJsonPath) {
    $packageJsonContent = Get-Content $packageJsonPath -Raw
    $packageJson = $packageJsonContent | ConvertFrom-Json
    
    # Converter para hashtable para facilitar modificações
    $packageHashtable = @{}
    $packageJson.PSObject.Properties | ForEach-Object {
        $packageHashtable[$_.Name] = $_.Value
    }
    
    # Adicionar scripts de produção
    if (-not $packageHashtable.ContainsKey('scripts')) {
        $packageHashtable['scripts'] = @{}
    }
    
    $scriptsHashtable = @{}
    if ($packageJson.scripts) {
        $packageJson.scripts.PSObject.Properties | ForEach-Object {
            $scriptsHashtable[$_.Name] = $_.Value
        }
    }
    
    # Adicionar novos scripts
    $scriptsHashtable['build:prod'] = "cross-env NODE_ENV=production GENERATE_SOURCEMAP=false npm run build"
    $scriptsHashtable['analyze'] = "npm run build:prod && npx bundle-analyzer build/static/js/*.js"
    $scriptsHashtable['deploy:prepare'] = "npm run security:audit && npm run build:secure"
    $scriptsHashtable['lighthouse'] = "lighthouse https://$DOMAIN --output html --output-path ./lighthouse-report.html"
    
    $packageHashtable['scripts'] = $scriptsHashtable
    
    # Adicionar dependências de desenvolvimento
    $devDepsHashtable = @{}
    if ($packageJson.devDependencies) {
        $packageJson.devDependencies.PSObject.Properties | ForEach-Object {
            $devDepsHashtable[$_.Name] = $_.Value
        }
    }
    
    $devDepsHashtable['cross-env'] = '^7.0.3'
    $devDepsHashtable['webpack-bundle-analyzer'] = '^4.9.0'
    
    $packageHashtable['devDependencies'] = $devDepsHashtable
    
    # Converter de volta para JSON e salvar
    $packageHashtable | ConvertTo-Json -Depth 10 | Out-File -FilePath $packageJsonPath -Encoding UTF8
    Write-Host "✅ Scripts do package.json atualizados" -ForegroundColor Green
}

# 3. CRIAR ARQUIVO DE CONFIGURAÇÃO DO WEBPACK PARA PRODUÇÃO
Write-Host "⚙️ Criando configuração do Webpack..." -ForegroundColor Blue

$webpackConfigProd = @"
const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  mode: 'production',
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\\\/]node_modules[\\\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
    usedExports: true,
    sideEffects: false,
  },
  plugins: [
    process.env.ANALYZE && new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
      reportFilename: 'bundle-report.html'
    })
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@config': path.resolve(__dirname, 'src/config'),
      '@services': path.resolve(__dirname, 'src/services')
    }
  }
};
"@

$webpackConfigProd | Out-File -FilePath "$FRONTEND_DIR/webpack.config.prod.js" -Encoding UTF8
Write-Host "✅ Configuração do Webpack criada" -ForegroundColor Green

# 4. CRIAR ARQUIVO .ENV.PRODUCTION OTIMIZADO
Write-Host "🌍 Criando arquivo .env.production..." -ForegroundColor Blue

$envProduction = @"
# 🚀 Configurações de Produção - Nautilus Automação
# ================================================

# Ambiente
REACT_APP_ENVIRONMENT=production
NODE_ENV=production

# API
REACT_APP_API_URL=https://$DOMAIN/api
REACT_APP_API_TIMEOUT=10000

# Segurança
REACT_APP_ENABLE_SECURITY_LOGS=false
REACT_APP_ENABLE_DEBUG=false
REACT_APP_ENABLE_DEVTOOLS=false

# Performance
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
REACT_APP_ENABLE_LAZY_LOADING=true

# Build
BUILD_PATH=build
PUBLIC_URL=https://$DOMAIN

# Monitoramento
REACT_APP_ENABLE_ERROR_REPORTING=true
REACT_APP_ENABLE_PERFORMANCE_TRACKING=true

# Cache
REACT_APP_CACHE_VERSION=1.0.0
REACT_APP_ENABLE_SERVICE_WORKER=true
"@

$envProduction | Out-File -FilePath "$FRONTEND_DIR/.env.production" -Encoding UTF8
Write-Host "✅ Arquivo .env.production criado" -ForegroundColor Green

# 5. CRIAR CONFIGURAÇÃO DO BACKEND PARA PRODUÇÃO
Write-Host "🐍 Criando configuração do backend..." -ForegroundColor Blue

$backendConfigProd = @"
# 🚀 Configurações de Produção - Backend
# ====================================

# Flask
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000

# Segurança
SECRET_KEY=your-super-secret-key-change-this-in-production
SECURITY_PASSWORD_SALT=your-security-salt-change-this

# Banco de Dados
DATABASE_URL=sqlite:///instance/site.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True, 'pool_recycle': 300}

# API
API_BASE_URL=https://$DOMAIN/api
API_VERSION=v1
API_RATE_LIMIT=100

# CORS
CORS_ORIGINS=https://$DOMAIN
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=Content-Type,Authorization,X-CSRF-Token

# Sessão
SESSION_TYPE=filesystem
SESSION_PERMANENT=False
SESSION_USE_SIGNER=True
SESSION_KEY_PREFIX=nautilus:
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict

# Logging
LOG_LEVEL=ERROR
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Performance
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Monitoramento
HEALTH_CHECK_ENABLED=True
METRICS_ENABLED=True

# Backup
BACKUP_ENABLED=True
BACKUP_INTERVAL=24
BACKUP_RETENTION=7
"@

$backendConfigProd | Out-File -FilePath "$BACKEND_DIR/.env.production" -Encoding UTF8
Write-Host "✅ Configuração do backend criada" -ForegroundColor Green

# 6. CRIAR SCRIPT DE OTIMIZAÇÃO DE IMAGENS
Write-Host "🖼️ Criando script de otimização..." -ForegroundColor Blue

$optimizeScript = @"
# 🖼️ Script de Otimização de Assets
# Nautilus Automação - Asset Optimization

Write-Host "🖼️ Otimizando assets para produção..." -ForegroundColor Blue

# Verificar se ImageMagick está instalado
if (-not (Get-Command "magick" -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  ImageMagick não encontrado. Instalando via Chocolatey..." -ForegroundColor Yellow
    
    if (Get-Command "choco" -ErrorAction SilentlyContinue) {
        choco install imagemagick -y
    } else {
        Write-Host "❌ Chocolatey não encontrado. Instale ImageMagick manualmente." -ForegroundColor Red
        Write-Host "   Download: https://imagemagick.org/script/download.php#windows" -ForegroundColor Cyan
        return
    }
}

# Otimizar imagens
`$assetsDir = "./frontend/src/assets"
if (Test-Path `$assetsDir) {
    Get-ChildItem -Path `$assetsDir -Recurse -Include *.jpg,*.jpeg,*.png | ForEach-Object {
        `$originalSize = `$_.Length
        
        Write-Host "🔧 Otimizando: `$(`$_.Name)" -ForegroundColor Blue
        
        # Otimizar imagem
        `$outputPath = `$_.FullName
        magick "`$(`$_.FullName)" -strip -quality 85 -resize "1920x1920>" "`$outputPath"
        
        `$newSize = (Get-Item `$outputPath).Length
        `$savings = [math]::Round(((`$originalSize - `$newSize) / `$originalSize) * 100, 1)
        
        Write-Host "   ✅ Reduzido em `$savings% (`$([math]::Round(`$originalSize/1KB, 1))KB → `$([math]::Round(`$newSize/1KB, 1))KB)" -ForegroundColor Green
    }
    
    Write-Host "✅ Otimização de imagens concluída" -ForegroundColor Green
} else {
    Write-Host "⚠️  Diretório de assets não encontrado" -ForegroundColor Yellow
}
"@

$optimizeScript | Out-File -FilePath "optimize-assets.ps1" -Encoding UTF8
Write-Host "✅ Script de otimização criado" -ForegroundColor Green

# 7. CRIAR CHECKLIST DE PRÉ-DEPLOY
Write-Host "📋 Criando checklist de pré-deploy..." -ForegroundColor Blue

$checklist = @"
📋 CHECKLIST PRÉ-DEPLOY - NAUTILUS AUTOMAÇÃO
==========================================

🔍 VERIFICAÇÕES OBRIGATÓRIAS:

[ ] 🔒 SEGURANÇA
    [ ] Chaves secretas alteradas (.env.production)
    [ ] CSP configurado corretamente
    [ ] Headers de segurança ativados
    [ ] Logs de debug desabilitados
    [ ] Console.log removido do código

[ ] 🚀 PERFORMANCE
    [ ] Imagens otimizadas (execute optimize-assets.ps1)
    [ ] Bundle analisado (npm run analyze)
    [ ] Sourcemaps desabilitados
    [ ] Lazy loading implementado
    [ ] Code splitting configurado

[ ] 🌐 CONFIGURAÇÃO
    [ ] Domínio correto em todas as configurações
    [ ] URLs da API atualizadas
    [ ] CORS configurado corretamente
    [ ] SSL/HTTPS configurado

[ ] 🧪 TESTES
    [ ] Testes unitários passando
    [ ] Testes de integração passando
    [ ] Build de produção funcionando
    [ ] Aplicação testada localmente

[ ] 📦 DEPLOY
    [ ] Backup do site atual realizado
    [ ] Dependências Python listadas
    [ ] Arquivos .htaccess criados
    [ ] Permissões configuradas

[ ] 📊 MONITORAMENTO
    [ ] Health check endpoint funcionando
    [ ] Error reporting configurado
    [ ] Logs de produção configurados
    [ ] Métricas de performance ativadas

🔧 COMANDOS ÚTEIS:

# Auditoria de segurança
npm run security:audit

# Build de produção
npm run build:secure

# Análise do bundle
npm run analyze

# Otimização de assets
.\optimize-assets.ps1

# Deploy automatizado
.\deploy-godaddy.ps1

# Verificação pós-deploy
.\verify-deploy.ps1

✅ APÓS O DEPLOY:

[ ] Site acessível via HTTPS
[ ] API respondendo corretamente
[ ] Login funcionando
[ ] Dashboard carregando
[ ] Sem erros no console
[ ] Performance satisfatória
[ ] Headers de segurança ativos
[ ] SSL válido

🎉 DEPLOY CONCLUÍDO COM SUCESSO!
"@

$checklist | Out-File -FilePath "CHECKLIST_PRE_DEPLOY.txt" -Encoding UTF8
Write-Host "✅ Checklist criado" -ForegroundColor Green

# 8. RESUMO FINAL
Write-Host "" -ForegroundColor White
Write-Host "🎉 CONFIGURAÇÃO PARA PRODUÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White
Write-Host "📁 ARQUIVOS CRIADOS:" -ForegroundColor Blue
Write-Host "   ✅ security.config.prod.js - Configurações de segurança" -ForegroundColor White
Write-Host "   ✅ .env.production (frontend) - Variáveis de ambiente" -ForegroundColor White
Write-Host "   ✅ .env.production (backend) - Configurações do servidor" -ForegroundColor White
Write-Host "   ✅ webpack.config.prod.js - Otimizações de build" -ForegroundColor White
Write-Host "   ✅ optimize-assets.ps1 - Otimização de imagens" -ForegroundColor White
Write-Host "   ✅ CHECKLIST_PRE_DEPLOY.txt - Lista de verificação" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Blue
Write-Host "1. Revise o arquivo CHECKLIST_PRE_DEPLOY.txt" -ForegroundColor White
Write-Host "2. Execute: .\optimize-assets.ps1" -ForegroundColor White
Write-Host "3. Execute: npm run security:audit" -ForegroundColor White
Write-Host "4. Execute: .\deploy-godaddy.ps1" -ForegroundColor White
Write-Host "5. Execute: .\verify-deploy.ps1 (após deploy)" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "🚀 Sua aplicação está pronta para produção!" -ForegroundColor Green

# Pausar para o usuário ler
Read-Host "Pressione Enter para finalizar"