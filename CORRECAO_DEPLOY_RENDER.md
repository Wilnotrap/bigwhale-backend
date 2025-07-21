# Correção de Erros no Deploy do Render

Este documento descreve os erros encontrados durante o deploy no Render e as soluções implementadas.

## Erros Identificados

1. **Tabela `active_signals` não encontrada**
   - Erro: `ERROR:services.auto_monitor_service:Erro ao buscar sinais do banco: (sqlite3.OperationalError) no such table: active_signals`
   - Causa: A tabela não foi criada durante a inicialização do banco de dados.

2. **Módulo `psycopg2` não encontrado**
   - Erro: `ERROR:app_corrigido:Erro ao criar banco PostgreSQL: No module named 'psycopg2'`
   - Causa: O pacote `psycopg2-binary` não está instalado ou não está no requirements.txt.

3. **Erros de roteamento na aplicação**
   - Erro: `ERROR:app_corrigido:Exception on / [HEAD]` e `ERROR:app_corrigido:Exception on / [GET]`
   - Causa: Problemas na configuração de rotas ou erros no tratamento de requisições.

## Soluções Implementadas

### 1. Criação da Tabela `active_signals`

Foi criado o script `criar_tabela_sinais.py` que:
- Verifica se a tabela `active_signals` existe
- Cria a tabela se não existir
- Confirma a estrutura da tabela

### 2. Instalação do `psycopg2`

- Adicionado `psycopg2-binary==2.9.9` ao arquivo `requirements.txt`
- Criado script que verifica e instala o pacote se necessário

### 3. Correção de Rotas

- Verificação e correção das rotas da aplicação
- Adição de uma rota principal (/) se não existir

## Como Aplicar as Correções

1. Execute o script de correção:
   ```
   python fix_deploy_errors.py
   ```

2. Crie a tabela de sinais:
   ```
   python criar_tabela_sinais.py
   ```

3. Inicialize o banco de dados:
   ```
   python init_db.py
   ```

4. Reinicie a aplicação no Render

Alternativamente, execute o script PowerShell que faz tudo isso:
```
.\deploy-render-fix.ps1
```

## Verificação

Após aplicar as correções, verifique:

1. Se a tabela `active_signals` foi criada:
   ```python
   from app import create_app
   from database import db
   from sqlalchemy import inspect
   
   app = create_app()
   with app.app_context():
       inspector = inspect(db.engine)
       print(inspector.get_table_names())
   ```

2. Se o módulo `psycopg2` está instalado:
   ```python
   import importlib.util
   print(importlib.util.find_spec('psycopg2') is not None)
   ```

3. Se as rotas estão funcionando:
   ```
   curl https://sua-aplicacao.onrender.com/api/health
   ```

## Prevenção de Problemas Futuros

1. Sempre execute `db.create_all()` na inicialização da aplicação
2. Mantenha o `requirements.txt` atualizado com todas as dependências
3. Implemente testes para verificar a existência de tabelas críticas
4. Adicione tratamento de erros para falhas de banco de dados