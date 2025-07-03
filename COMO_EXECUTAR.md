# 🚀 Como Executar o Sistema Bitget

## Opção 1: Execução Automática (Recomendado)

### Windows - Script Batch
```bash
# Clique duplo no arquivo ou execute no terminal:
executar_sistema.bat
```

### Windows - PowerShell
```powershell
# Execute no PowerShell:
.\executar_sistema.ps1
```

## Opção 2: Execução Manual

### 1. Iniciar Backend

```bash
# Navegar para o diretório backend
cd backend

# Corrigir banco de dados (opcional)
python fix_sistema.py

# Iniciar servidor Flask
python app.py
```

O backend estará disponível em: **http://localhost:5000**

### 2. Iniciar Frontend (Nova janela/terminal)

```bash
# Navegar para o diretório frontend
cd frontend

# Instalar dependências (apenas na primeira vez)
npm install

# Iniciar servidor React
npm start
```

O frontend estará disponível em: **http://localhost:3000**

## 📋 Pré-requisitos

- ✅ **Python 3.8+** instalado
- ✅ **Node.js 16+** e npm instalados
- ✅ Dependências Python instaladas (`pip install -r requirements.txt`)

## 🔐 Credenciais de Teste

| Email | Senha | Tipo |
|-------|-------|------|
| admin@teste.com | 123456 | Administrador |
| user@teste.com | 123456 | Usuário |
| teste@teste.com | 123456 | Teste |

## 🌐 URLs do Sistema

- **Frontend (Interface)**: http://localhost:3000
- **Backend (API)**: http://localhost:5000
- **Admin Panel**: http://localhost:3000/admin

## 🔧 Solução de Problemas

### Backend não inicia
```bash
# Verificar se Python está instalado
python --version

# Instalar dependências
pip install -r requirements.txt

# Verificar se a porta 5000 está livre
netstat -an | findstr :5000
```

### Frontend não inicia
```bash
# Verificar se Node.js está instalado
node --version
npm --version

# Limpar cache e reinstalar
npm cache clean --force
rm -rf node_modules
npm install

# Verificar se a porta 3000 está livre
netstat -an | findstr :3000
```

### Erro de CORS
O sistema já está configurado para resolver problemas de CORS automaticamente.

### Banco de dados corrompido
```bash
# Deletar banco e recriar
cd backend
rm instance/site.db
python fix_sistema.py
```

## 📁 Estrutura do Projeto

```
bitget/
├── backend/          # Servidor Flask (Python)
│   ├── app.py        # Aplicação principal
│   ├── fix_sistema.py # Script de correção do BD
│   └── ...
├── frontend/         # Interface React
│   ├── package.json  # Dependências Node.js
│   └── ...
├── executar_sistema.bat  # Script Windows
├── executar_sistema.ps1  # Script PowerShell
└── COMO_EXECUTAR.md     # Este arquivo
```

## 💡 Dicas

1. **Sempre inicie o backend primeiro**, depois o frontend
2. **Aguarde alguns segundos** para os servidores iniciarem completamente
3. **Use Ctrl+C** para parar os servidores nos terminais
4. **Verifique os logs** em caso de erro nos terminais
5. **Limpe o cache do navegador** se houver problemas de carregamento

---

✅ **Sistema pronto para uso!** Acesse http://localhost:3000 e faça login com as credenciais acima.