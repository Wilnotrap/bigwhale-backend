# 🔐 Sistema Seguro de Gerenciamento de Credenciais da API

## Visão Geral

Este sistema fornece uma solução completa e segura para gerenciar credenciais da API Bitget, incluindo:

- **Salvamento seguro** com criptografia AES-256
- **Monitoramento contínuo** da integridade das credenciais
- **Backup automático** antes de cada alteração
- **Restauração automática** em caso de problemas
- **Interface web moderna** para gerenciamento
- **API REST segura** para integração

## 🚀 Instalação e Configuração

### 1. Dependências

Certifique-se de que as seguintes dependências estão instaladas:

```bash
pip install flask sqlalchemy python-dotenv psutil
```

### 2. Configuração do Ambiente

Configure as variáveis de ambiente no arquivo `.env`:

```env
# Chave de criptografia (deve ter 32 bytes)
AES_ENCRYPTION_KEY=chave-criptografia-api-bitget-nautilus-sistema-seguro-123456789

# Configurações do Flask
FLASK_SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=production

# Configurações do banco de dados
DATABASE_URL=sqlite:///instance/site.db
```

### 3. Estrutura de Arquivos

```
backend/
├── services/
│   ├── credential_monitor.py      # Serviço de monitoramento
│   └── secure_api_service.py      # API REST segura
├── utils/
│   ├── security.py                # Funções de criptografia
│   └── api_persistence.py         # Persistência e backup
├── models/
│   └── user.py                    # Modelo do usuário
├── start_credential_services.py   # Script de inicialização
└── logs/                          # Logs do sistema
    └── credential_monitor.log

static/js/
└── secure_credentials.js          # JavaScript do frontend

templates/
└── secure_credentials_form.html   # Template HTML

backups/api_credentials/           # Backups das credenciais
├── user_1_credentials_*.json
└── user_2_credentials_*.json
```

## 🎯 Como Usar

### 1. Iniciar os Serviços

#### Opção A: Script Completo (Recomendado)

```bash
cd "c:\Nautilus Aut\22\backend"
python start_credential_services.py
```

Este script inicia:
- Monitoramento contínuo (verificação a cada 1 minuto)
- API REST segura (porta 5001)
- Logs detalhados

#### Opção B: Serviços Individuais

```bash
# Apenas monitoramento
python -m services.credential_monitor

# Apenas API
python -m services.secure_api_service
```

### 2. Interface Web

Acesse o formulário seguro de credenciais:

```
http://localhost:5001/secure_credentials_form.html
```

### 3. Funcionalidades Principais

#### Salvar Credenciais

1. Preencha o formulário com:
   - API Key da Bitget
   - API Secret da Bitget
   - Passphrase da Bitget

2. Clique em "Salvar Credenciais com Segurança"

3. O sistema automaticamente:
   - Valida o formato das credenciais
   - Criptografa com AES-256
   - Cria backup das credenciais anteriores
   - Salva no banco de dados
   - Inicia monitoramento

#### Monitoramento Automático

O sistema verifica automaticamente:
- **A cada 1 minuto**: Integridade das credenciais
- **Em tempo real**: Status da criptografia
- **Continuamente**: Capacidade de descriptografia

#### Restauração Automática

Em caso de problemas:
1. O sistema detecta automaticamente falhas
2. Busca o backup mais recente
3. Restaura as credenciais
4. Valida a restauração
5. Notifica o resultado

## 🔧 API REST

### Endpoints Disponíveis

#### Salvar Credenciais
```http
POST /api/credentials/save
Content-Type: application/json

{
  "api_key": "sua_api_key",
  "api_secret": "sua_api_secret",
  "passphrase": "sua_passphrase"
}
```

#### Verificar Status
```http
GET /api/credentials/status
```

#### Validar Credenciais
```http
GET /api/credentials/validate
```

#### Testar Conexão
```http
POST /api/credentials/test-connection
```

#### Listar Backups
```http
GET /api/credentials/backups
```

#### Restaurar Credenciais
```http
POST /api/credentials/restore
Content-Type: application/json

{
  "backup_filename": "user_1_credentials_20241201_120000.json" // Opcional
}
```

#### Verificação Forçada
```http
POST /api/credentials/force-check
```

#### Status do Monitor
```http
GET /api/monitor/status
```

## 🛡️ Segurança

### Criptografia

- **Algoritmo**: AES-256 em modo CBC
- **Chave**: Derivada de PBKDF2 com salt aleatório
- **IV**: Gerado aleatoriamente para cada operação
- **MAC**: Verificação de integridade com HMAC-SHA256

### Backup

- **Automático**: Antes de cada alteração
- **Formato**: JSON criptografado
- **Localização**: `backups/api_credentials/`
- **Retenção**: 5 backups mais recentes por usuário
- **Nomenclatura**: `user_{id}_credentials_{timestamp}.json`

### Logs

- **Localização**: `logs/credential_monitor.log`
- **Rotação**: Automática por tamanho
- **Níveis**: INFO, WARNING, ERROR
- **Conteúdo**: Operações, status, erros (sem dados sensíveis)

## 🔍 Monitoramento

### Verificações Automáticas

1. **Integridade da Criptografia**
   - Verifica se os dados podem ser descriptografados
   - Detecta corrupção ou alteração de chaves

2. **Disponibilidade das Credenciais**
   - Confirma que todas as credenciais estão presentes
   - Valida formato e estrutura

3. **Consistência do Sistema**
   - Verifica configuração da chave AES
   - Monitora saúde do banco de dados

### Alertas e Notificações

- **Interface Web**: Status em tempo real
- **Logs**: Registro detalhado de eventos
- **Console**: Mensagens importantes
- **API**: Endpoints de status

## 🚨 Solução de Problemas

### Problema: "MAC check failed"

**Causa**: Chave de criptografia incorreta ou dados corrompidos

**Solução**:
1. O sistema tenta automaticamente chaves de fallback
2. Se falhar, restaura do backup mais recente
3. Se necessário, solicita novas credenciais

### Problema: Credenciais não salvam

**Verificar**:
1. Permissões de escrita no banco de dados
2. Configuração da chave AES
3. Logs para erros específicos

### Problema: Monitoramento não funciona

**Verificar**:
1. Se o serviço está rodando: `python start_credential_services.py`
2. Logs em `logs/credential_monitor.log`
3. Status via API: `GET /api/monitor/status`

### Problema: Backup não restaura

**Verificar**:
1. Existência dos arquivos em `backups/api_credentials/`
2. Permissões de leitura
3. Integridade dos arquivos de backup

## 📊 Comandos CLI

```bash
# Verificar status
flask check-credentials-now

# Iniciar monitoramento
flask start-credential-monitor

# Parar monitoramento
flask stop-credential-monitor
```

## 🔄 Integração com Sistema Existente

### 1. Modificar Rotas Existentes

Substitua o salvamento direto de credenciais por:

```python
from services.credential_monitor import credential_monitor

# Em vez de salvar diretamente
success = credential_monitor.secure_save_credentials(
    user_id, api_key, api_secret, passphrase
)
```

### 2. Verificar Credenciais

```python
# Verificar se as credenciais estão válidas
result = credential_monitor.check_user_credentials(user)
if result['valid']:
    # Credenciais OK
else:
    # Problema detectado: result['error']
```

### 3. Inicialização da Aplicação

```python
from services.credential_monitor import credential_monitor

app = Flask(__name__)
credential_monitor.init_app(app)

# Iniciar monitoramento
with app.app_context():
    credential_monitor.start_monitoring()
```

## 📈 Métricas e Performance

- **Verificação**: ~100ms por usuário
- **Backup**: ~50ms por operação
- **Criptografia**: ~10ms por credencial
- **Restauração**: ~200ms por usuário

## 🔮 Próximas Funcionalidades

- [ ] Dashboard de monitoramento
- [ ] Notificações por email
- [ ] Backup em nuvem
- [ ] Auditoria avançada
- [ ] Múltiplas exchanges
- [ ] API webhooks

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique os logs em `logs/credential_monitor.log`
2. Teste os endpoints da API
3. Consulte este README
4. Verifique a configuração do ambiente

---

**⚠️ Importante**: Mantenha sempre backups das suas credenciais e da chave de criptografia em local seguro!