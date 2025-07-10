#!/usr/bin/env node
/**
 * Script de teste de segurança para verificar vulnerabilidades
 * Verifica exposição de dados sensíveis e configurações inseguras
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Padrões de vulnerabilidades de segurança
const SECURITY_PATTERNS = {
  // Exposição de dados sensíveis
  sensitiveData: [
    /console\.log\([^)]*(?:password|senha|token|api[_-]?key|secret|credential)[^)]*\)/gi,
    /console\.log\([^)]*(?:balance|saldo|profit|lucro|loss|prejuizo|pnl)[^)]*\)/gi,
    /console\.log\([^)]*(?:email|phone|telefone|cpf|cnpj|user[_-]?id)[^)]*\)/gi
  ],
  
  // Hardcoded secrets
  hardcodedSecrets: [
    /(?:api[_-]?key|token|secret|password)\s*[=:]\s*['"][^'"]{8,}['"]/gi,
    /(?:Bearer|Basic)\s+[A-Za-z0-9+/=]{20,}/gi
  ],
  
  // URLs e endpoints expostos
  exposedEndpoints: [
    /https?:\/\/[^\s'"]+(?:api[_-]?key|token|secret)[^\s'"]*['"]?/gi,
    /localhost:\d+\/api\/[^\s'"]+/gi
  ],
  
  // Configurações inseguras
  insecureConfig: [
    /eval\s*\(/gi,
    /innerHTML\s*=/gi,
    /document\.write\s*\(/gi,
    /dangerouslySetInnerHTML/gi
  ],
  
  // Debug em produção
  debugInProduction: [
    /console\.(?:log|debug|trace|table)\s*\(/gi,
    /debugger\s*;/gi
  ]
};

// Configurações que devem estar presentes
const REQUIRED_SECURITY_CONFIG = {
  packageJson: {
    scripts: {
      'build:clean': 'node scripts/remove-logs.js',
      'test:security': 'node scripts/test-security.js'
    }
  },
  envFiles: [
    '.env.production',
    '.env.local'
  ]
};

class SecurityTester {
  constructor() {
    this.vulnerabilities = [];
    this.warnings = [];
    this.passed = [];
  }
  
  addVulnerability(type, file, line, description) {
    this.vulnerabilities.push({ type, file, line, description });
  }
  
  addWarning(type, file, description) {
    this.warnings.push({ type, file, description });
  }
  
  addPassed(description) {
    this.passed.push(description);
  }
  
  testFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      // Testa cada padrão de vulnerabilidade
      Object.entries(SECURITY_PATTERNS).forEach(([category, patterns]) => {
        patterns.forEach(pattern => {
          lines.forEach((line, index) => {
            if (pattern.test(line)) {
              this.addVulnerability(
                category,
                filePath,
                index + 1,
                `Padrão inseguro encontrado: ${line.trim()}`
              );
            }
          });
        });
      });
      
    } catch (error) {
      this.addWarning('fileAccess', filePath, `Erro ao ler arquivo: ${error.message}`);
    }
  }
  
  testPackageJson() {
    const packagePath = path.join(__dirname, '../package.json');
    try {
      const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      
      // Verifica scripts de segurança
      const requiredScripts = REQUIRED_SECURITY_CONFIG.packageJson.scripts;
      Object.entries(requiredScripts).forEach(([script, command]) => {
        if (!packageJson.scripts || !packageJson.scripts[script]) {
          this.addVulnerability(
            'missingConfig',
            packagePath,
            0,
            `Script de segurança ausente: ${script}`
          );
        } else {
          this.addPassed(`Script de segurança presente: ${script}`);
        }
      });
      
      // Verifica dependências de segurança
      const securityDeps = ['helmet', 'cors', 'express-rate-limit'];
      securityDeps.forEach(dep => {
        if (!packageJson.dependencies || !packageJson.dependencies[dep]) {
          this.addWarning(
            'missingDependency',
            packagePath,
            `Dependência de segurança recomendada ausente: ${dep}`
          );
        }
      });
      
    } catch (error) {
      this.addVulnerability(
        'configError',
        packagePath,
        0,
        `Erro ao ler package.json: ${error.message}`
      );
    }
  }
  
  testEnvFiles() {
    REQUIRED_SECURITY_CONFIG.envFiles.forEach(envFile => {
      const envPath = path.join(__dirname, `../${envFile}`);
      if (!fs.existsSync(envPath)) {
        this.addWarning(
          'missingConfig',
          envPath,
          `Arquivo de configuração ausente: ${envFile}`
        );
      } else {
        this.addPassed(`Arquivo de configuração presente: ${envFile}`);
        
        // Verifica se não há secrets hardcoded
        try {
          const content = fs.readFileSync(envPath, 'utf8');
          if (content.includes('password=') || content.includes('secret=')) {
            this.addVulnerability(
              'hardcodedSecrets',
              envPath,
              0,
              'Possível secret hardcoded em arquivo de ambiente'
            );
          }
        } catch (error) {
          this.addWarning('fileAccess', envPath, `Erro ao ler ${envFile}`);
        }
      }
    });
  }
  
  testLoggerImplementation() {
    const loggerPath = path.join(__dirname, '../src/utils/logger.js');
    if (fs.existsSync(loggerPath)) {
      const content = fs.readFileSync(loggerPath, 'utf8');
      
      // Verifica se o logger seguro está implementado
      if (content.includes('sanitizeData') && content.includes('SENSITIVE_KEYWORDS')) {
        this.addPassed('Logger seguro implementado corretamente');
      } else {
        this.addVulnerability(
          'insecureLogger',
          loggerPath,
          0,
          'Logger não implementa sanitização de dados sensíveis'
        );
      }
      
      // Verifica se console é sobrescrito em produção
      if (content.includes('console.log = () => {}')) {
        this.addPassed('Console desabilitado em produção');
      } else {
        this.addVulnerability(
          'productionLogs',
          loggerPath,
          0,
          'Console não está desabilitado em produção'
        );
      }
    } else {
      this.addVulnerability(
        'missingLogger',
        loggerPath,
        0,
        'Logger seguro não encontrado'
      );
    }
  }
  
  runTests() {
    console.log('🔒 Iniciando testes de segurança...');
    
    // Testa arquivos JavaScript/JSX
    const srcPattern = path.join(__dirname, '../src/**/*.{js,jsx}');
    const files = glob.sync(srcPattern);
    
    console.log(`📁 Testando ${files.length} arquivos...`);
    files.forEach(file => this.testFile(file));
    
    // Testa configurações
    this.testPackageJson();
    this.testEnvFiles();
    this.testLoggerImplementation();
    
    this.generateReport();
  }
  
  generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 RELATÓRIO DE SEGURANÇA');
    console.log('='.repeat(60));
    
    // Vulnerabilidades críticas
    if (this.vulnerabilities.length > 0) {
      console.log('\n🚨 VULNERABILIDADES CRÍTICAS:');
      this.vulnerabilities.forEach((vuln, index) => {
        console.log(`${index + 1}. [${vuln.type.toUpperCase()}] ${vuln.file}:${vuln.line}`);
        console.log(`   ${vuln.description}`);
      });
    }
    
    // Avisos
    if (this.warnings.length > 0) {
      console.log('\n⚠️  AVISOS:');
      this.warnings.forEach((warning, index) => {
        console.log(`${index + 1}. [${warning.type.toUpperCase()}] ${warning.file}`);
        console.log(`   ${warning.description}`);
      });
    }
    
    // Testes aprovados
    if (this.passed.length > 0) {
      console.log('\n✅ TESTES APROVADOS:');
      this.passed.forEach((test, index) => {
        console.log(`${index + 1}. ${test}`);
      });
    }
    
    // Resumo
    console.log('\n' + '='.repeat(60));
    console.log('📈 RESUMO:');
    console.log(`🚨 Vulnerabilidades: ${this.vulnerabilities.length}`);
    console.log(`⚠️  Avisos: ${this.warnings.length}`);
    console.log(`✅ Aprovados: ${this.passed.length}`);
    
    const score = Math.max(0, 100 - (this.vulnerabilities.length * 20) - (this.warnings.length * 5));
    console.log(`🎯 Score de Segurança: ${score}/100`);
    
    if (this.vulnerabilities.length === 0) {
      console.log('\n🛡️  PARABÉNS! Nenhuma vulnerabilidade crítica encontrada!');
    } else {
      console.log('\n🔧 AÇÃO NECESSÁRIA: Corrija as vulnerabilidades antes do deploy!');
      process.exit(1);
    }
  }
}

if (require.main === module) {
  const tester = new SecurityTester();
  tester.runTests();
}

module.exports = SecurityTester;