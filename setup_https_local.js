// Script para configurar HTTPS local facilmente
const fs = require('fs');
const path = require('path');

// Configuração para o frontend React
const reactHTTPSConfig = `
// No package.json, adicionar:
"scripts": {
  "start": "HTTPS=true react-scripts start",
  "start-windows": "set HTTPS=true && react-scripts start"
}

// Ou criar arquivo .env na pasta frontend:
HTTPS=true
SSL_CRT_FILE=certs/localhost.crt
SSL_KEY_FILE=certs/localhost.key
`;

// Instruções para gerar certificados locais
const certificateInstructions = `
# INSTRUÇÕES PARA CERTIFICADOS HTTPS LOCAL

## Opção 1: mkcert (Recomendado)
1. Instalar mkcert: https://github.com/FiloSottile/mkcert
2. cd frontend
3. mkdir certs
4. mkcert -install
5. mkcert -key-file certs/localhost.key -cert-file certs/localhost.crt localhost 127.0.0.1

## Opção 2: OpenSSL
cd frontend && mkdir certs
openssl req -x509 -newkey rsa:2048 -keyout certs/localhost.key -out certs/localhost.crt -days 365 -nodes -subj "/CN=localhost"

## Opção 3: React Dev Server (Mais Simples)
Apenas adicionar HTTPS=true no .env funciona para desenvolvimento
`;

console.log('📋 CONFIGURAÇÃO HTTPS LOCAL CRIADA');
console.log('✅ Arquivo: setup_https_local.js');
console.log('📄 Verificar arquivo para instruções completas');

// Salvar instruções em arquivo
fs.writeFileSync('INSTRUCOES_HTTPS_LOCAL.md', certificateInstructions);
console.log('📄 Instruções salvas em: INSTRUCOES_HTTPS_LOCAL.md'); 