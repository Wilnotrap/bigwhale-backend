# BigWhale Backend - Deploy

Este repositório contém apenas os arquivos necessários para deploy no Render.

## Estrutura

- `backend/` - Código Python da API
- `requirements.txt` - Dependências Python
- `runtime.txt` - Versão do Python
- `Procfile` - Comando de inicialização
- `render.yaml` - Configuração do Render

## Deploy

1. Conecte este repositório ao Render
2. Configure as variáveis de ambiente:
   - `FLASK_SECRET_KEY`
   - `AES_ENCRYPTION_KEY`
   - `DATABASE_URL` (PostgreSQL)

## Endpoints Principais

- `GET /api/health` - Health check
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registro
- `GET /api/auth/profile` - Perfil do usuário

## Última atualização

2025-07-15 23:06:20