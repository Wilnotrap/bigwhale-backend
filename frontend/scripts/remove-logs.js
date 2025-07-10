#!/usr/bin/env node
/**
 * Script para remover logs sensíveis antes do build de produção
 * Protege contra exposição de dados no console
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Padrões de logs perigosos que devem ser removidos
const DANGEROUS_PATTERNS = [
  /console\.log\([^)]*(?:api[_-]?key|password|token|secret|credential)[^)]*\)/gi,
  /console\.log\([^)]*(?:user|email|phone|cpf|cnpj)[^)]*\)/gi,
  /console\.log\([^)]*(?:balance|profit|loss|pnl)[^)]*\)/gi,
  /console\.debug\(/gi,
  /console\.trace\(/gi,
  /console\.table\(/gi
];

// Padrões seguros que podem permanecer
const SAFE_PATTERNS = [
  /logger\.(info|error|warn|secure)\(/gi,
  /console\.(error|warn)\(\s*['"`][^'"`,]*['"`]\s*\)/gi // Apenas strings literais
];

function cleanFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    
    // Remove padrões perigosos
    DANGEROUS_PATTERNS.forEach(pattern => {
      if (pattern.test(content)) {
        content = content.replace(pattern, '// [LOG REMOVIDO POR SEGURANÇA]');
        modified = true;
      }
    });
    
    // Remove console.log genéricos em produção
    const genericConsoleLog = /console\.log\([^)]*\);?/gi;
    if (genericConsoleLog.test(content)) {
      // Verifica se não é um padrão seguro
      const lines = content.split('\n');
      const cleanedLines = lines.map(line => {
        if (genericConsoleLog.test(line)) {
          // Verifica se é um padrão seguro
          const isSafe = SAFE_PATTERNS.some(safePattern => safePattern.test(line));
          if (!isSafe) {
            return line.replace(genericConsoleLog, '// [LOG REMOVIDO POR SEGURANÇA]');
          }
        }
        return line;
      });
      content = cleanedLines.join('\n');
      modified = true;
    }
    
    if (modified) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✓ Logs removidos de: ${filePath}`);
    }
  } catch (error) {
    console.error(`✗ Erro ao processar ${filePath}:`, error.message);
  }
}

function main() {
  console.log('🔒 Iniciando remoção de logs sensíveis...');
  
  // Encontra todos os arquivos JS/JSX no src
  const srcPattern = path.join(__dirname, '../src/**/*.{js,jsx}');
  const files = glob.sync(srcPattern);
  
  console.log(`📁 Encontrados ${files.length} arquivos para verificar`);
  
  files.forEach(cleanFile);
  
  console.log('✅ Processo de limpeza concluído!');
  console.log('🛡️ Aplicação protegida contra vazamento de dados no console');
}

if (require.main === module) {
  main();
}

module.exports = { cleanFile, main };