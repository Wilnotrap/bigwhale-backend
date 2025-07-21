# Instruções para Correção Imediata no Render

Este documento contém instruções para corrigir os erros que estão ocorrendo no ambiente Render.

## Erros Identificados

1. **Tabela `active_signals` não encontrada**
   - Erro: `ERROR:services.auto_monitor_service:Erro ao buscar sinais do banco: (sqlite3.OperationalError) no such table: active_signals`

2. **Módulo `psycopg2` não encontrado**
   - Erro: `ERROR:app_corrigido:Erro ao criar banco PostgreSQL: No module named 'psycopg2'`

3. **Erros de roteamento na aplicação**
   - Erro: `ERROR:app_corrigido:Exception on / [HEAD]` e outros erros de rota

## Opções de Correção

### Opção 1: Correção via Shell Console do Render

1. Acesse o console do Render para seu serviço
2. Execute os seguintes comandos:

```bash
# Instalar psycopg2
pip install psycopg2-binary==2.9.9

# Baixar o script de correção do GitHub
curl -O https://raw.githubusercontent.com/Wilnotrap/bigwhale-backend/main/correcao_direta_render.py

# Executar o script de correção
python correcao_direta_render.py

# Reiniciar o serviço
# (Use o botão de reiniciar no painel do Render)
```

### Opção 2: Correção via Script Shell

1. Acesse o console do Render para seu serviço
2. Execute os seguintes comandos:

```bash
# Baixar o script de correção do GitHub
curl -O https://raw.githubusercontent.com/Wilnotrap/bigwhale-backend/main/corrigir_render_agora.sh

# Dar permissão de execução
chmod +x corrigir_render_agora.sh

# Executar o script
./corrigir_render_agora.sh

# Reiniciar o serviço
# (Use o botão de reiniciar no painel do Render)
```

### Opção 3: Correção Manual

Se as opções acima não funcionarem, siga estes passos manualmente:

1. Instale o pacote psycopg2:
   ```bash
   pip install psycopg2-binary==2.9.9
   ```

2. Crie a tabela active_signals:
   ```bash
   python -c "
   from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
   from sqlalchemy.ext.declarative import declarative_base
   import os

   # Definir o caminho do banco SQLite no Render
   db_path = '/tmp/site.db'

   # Criar engine
   engine = create_engine(f'sqlite:///{db_path}')
   Base = declarative_base()

   # Definir modelo ActiveSignal
   class ActiveSignal(Base):
       __tablename__ = 'active_signals'
       
       id = Column(Integer, primary_key=True)
       symbol = Column(String(20), nullable=False)
       side = Column(String(10), nullable=False)
       entry_price = Column(Float, nullable=False)
       stop_loss = Column(Float, nullable=True)
       take_profit = Column(Float, nullable=True)
       status = Column(String(20), default='active')
       created_at = Column(DateTime)
       closed_at = Column(DateTime, nullable=True)
       user_id = Column(Integer, nullable=True)
       targets = Column(String(500), nullable=True)
       targets_hit = Column(Integer, default=0)

   # Criar tabela
   Base.metadata.create_all(engine)
   print('Tabela active_signals criada com sucesso!')
   "
   ```

3. Inicialize o banco de dados:
   ```bash
   python init_db.py
   ```

4. Reinicie o serviço no Render

## Verificação

Após aplicar as correções, verifique se os erros foram resolvidos:

1. Acesse a URL do seu serviço no Render
2. Verifique os logs para confirmar que não há mais erros
3. Teste os endpoints da API para garantir que estão funcionando corretamente

## Prevenção de Problemas Futuros

Para evitar problemas semelhantes no futuro:

1. Sempre execute `db.create_all()` na inicialização da aplicação
2. Mantenha o `requirements.txt` atualizado com todas as dependências
3. Implemente verificações de integridade do banco na inicialização
4. Adicione tratamento de erros mais robusto para falhas de conexão