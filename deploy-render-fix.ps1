# Script para corrigir problemas de deploy no Render
# Executa as correções necessárias e reinicia a aplicação

Write-Host "=== INICIANDO CORREÇÃO DE DEPLOY NO RENDER ===" -ForegroundColor Cyan

# Verificar se psycopg2 está instalado
Write-Host "Verificando dependências..." -ForegroundColor Yellow
pip install psycopg2-binary

# Executar script de correção
Write-Host "Executando script de correção..." -ForegroundColor Yellow
python fix_deploy_errors.py

# Criar tabela de sinais
Write-Host "Criando tabela de sinais..." -ForegroundColor Yellow
python criar_tabela_sinais.py

# Inicializar banco de dados
Write-Host "Inicializando banco de dados..." -ForegroundColor Yellow
python init_db.py

Write-Host "=== CORREÇÃO DE DEPLOY CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Para aplicar as correções, reinicie a aplicação no Render" -ForegroundColor Yellow