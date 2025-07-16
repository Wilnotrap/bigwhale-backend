# 🚀 Nautilus Backend - API de Trading

## 📋 Sobre

Backend da plataforma Nautilus Automação, uma API RESTful completa para trading automatizado integrada com a Bitget.

## ✅ Características

- 🔐 **Autenticação JWT** segura
- 🗄️ **PostgreSQL** para produção  
- 🔒 **Criptografia AES-256** para credenciais API
- 🌐 **WebSocket** real-time com Bitget
- 📊 **Endpoints completos** para trading
- 🛡️ **Middleware de segurança** avançado

## 🏗️ Estrutura

```
backend/
├── api/           # Endpoints da API
├── auth/          # Sistema de autenticação
├── middleware/    # Middlewares de segurança
├── models/        # Modelos do banco de dados
├── services/      # Serviços de negócio
├── utils/         # Utilitários
├── websocket/     # WebSocket Bitget
├── app.py         # Aplicação principal
└── requirements.txt
```

## 🚀 Instalação

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env

# 3. Executar aplicação
python app.py
```

## 🌐 Deploy

### Render.com
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`
- **Environment:** Python 3.9+

### Variáveis de Ambiente

```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
BITGET_API_URL=https://api.bitget.com
ENCRYPTION_KEY=your-encryption-key
```

## 📡 Endpoints Principais

- `POST /auth/login` - Autenticação
- `POST /auth/register` - Cadastro
- `GET /api/profile` - Perfil do usuário
- `POST /api/reconnect-api` - Reconectar API Bitget
- `GET /api/dashboard` - Dados do dashboard
- `GET /api/trades` - Histórico de trades

## 🔧 Tecnologias

- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Banco de dados
- **JWT** - Autenticação
- **Cryptography** - Criptografia
- **WebSocket** - Tempo real
