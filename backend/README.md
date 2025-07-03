# BigWhale Backend - Railway Deploy

Este é o backend do sistema BigWhale hospedado no Railway.

## Funcionalidades

- API REST para autenticação de usuários
- Integração com Bitget API
- Dashboard de trading
- Gestão de usuários e sessões

## Endpoints Principais

- `GET /api/health` - Health check
- `GET /api/test` - Teste básico
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registro
- `GET /api/auth/session` - Verificar sessão
- `GET /api/dashboard/*` - Endpoints do dashboard

## Tecnologias

- Python 3.11+
- Flask
- SQLAlchemy
- Gunicorn
- Railway (hosting)

## Deploy

O deploy é automático via Railway quando há push para a branch main.

## Variáveis de Ambiente

- `FLASK_SECRET_KEY` - Chave secreta do Flask
- `AES_ENCRYPTION_KEY` - Chave para criptografia das APIs

## Frontend

O frontend está hospedado em: https://bwhale.site 