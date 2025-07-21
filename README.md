# BigWhale Backend

Backend para o sistema de trading BigWhale com suporte a conta demo.

## Funcionalidades

- API simulada da Bitget para conta demo
- Endpoints para gerenciamento de posições
- Estatísticas de trading em tempo real
- Autenticação de usuários
- Suporte a PostgreSQL para produção

## Deploy no Render

1. Conecte ao repositório GitHub
2. Configure as variáveis de ambiente:
   - `FLASK_SECRET_KEY`: Chave secreta forte
   - `DATABASE_URL`: URL do PostgreSQL (fornecida pelo Render)
   - `CORS_ORIGINS`: Domínios permitidos
   - `ENVIRONMENT`: production
   - `FLASK_ENV`: production

## API Endpoints

### Autenticação
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/logout` - Logout de usuário

### Conta Demo
- `GET /api/demo/balance` - Obter saldo da conta demo
- `GET /api/demo/positions` - Obter posições abertas
- `GET /api/demo/stats` - Obter estatísticas de trading

### Saúde do Sistema
- `GET /api/health` - Verificar status do sistema

## Conta Demo

- **Email**: `financeiro@lexxusadm.com.br`
- **Senha**: `FinanceiroDemo2025@`
- **Saldo**: $600 USD
