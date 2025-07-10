# 🔒 Script para Correção de Vulnerabilidades de Segurança
# Nautilus Automação - Security Fix

Write-Host "🔒 Corrigindo Vulnerabilidades de Segurança - Nautilus Automação" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Yellow

# Navegar para o diretório do frontend
Set-Location "./frontend"

Write-Host "📍 Diretório atual: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Verificar vulnerabilidades atuais
Write-Host "🔍 Verificando vulnerabilidades atuais..." -ForegroundColor Blue
npm audit

Write-Host ""
Write-Host "🛠️ OPÇÕES DE CORREÇÃO:" -ForegroundColor Yellow
Write-Host "1. Correção automática (segura)" -ForegroundColor White
Write-Host "2. Correção forçada (pode quebrar compatibilidade)" -ForegroundColor White
Write-Host "3. Atualização manual de dependências" -ForegroundColor White
Write-Host "4. Pular correções (não recomendado)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Escolha uma opção (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🔧 Executando correção automática..." -ForegroundColor Green
        npm audit fix
        
        Write-Host "📊 Verificando resultado..." -ForegroundColor Blue
        npm audit
    }
    
    "2" {
        Write-Host "⚠️ ATENÇÃO: Esta opção pode quebrar a compatibilidade!" -ForegroundColor Red
        $confirm = Read-Host "Tem certeza? (s/n)"
        
        if ($confirm -eq "s" -or $confirm -eq "S" -or $confirm -eq "sim") {
            Write-Host "🔧 Executando correção forçada..." -ForegroundColor Yellow
            npm audit fix --force
            
            Write-Host "📊 Verificando resultado..." -ForegroundColor Blue
            npm audit
            
            Write-Host "⚠️ IMPORTANTE: Teste a aplicação após esta correção!" -ForegroundColor Red
        } else {
            Write-Host "❌ Operação cancelada." -ForegroundColor Yellow
        }
    }
    
    "3" {
        Write-Host "📋 VULNERABILIDADES IDENTIFICADAS:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. brace-expansion (1.0.0 - 1.1.11 || 2.0.0 - 2.0.1)" -ForegroundColor Red
        Write-Host "   - Tipo: Regular Expression Denial of Service" -ForegroundColor White
        Write-Host "   - Severidade: Moderada" -ForegroundColor White
        Write-Host ""
        Write-Host "2. nth-check (<2.0.1)" -ForegroundColor Red
        Write-Host "   - Tipo: Inefficient Regular Expression Complexity" -ForegroundColor White
        Write-Host "   - Severidade: Alta" -ForegroundColor White
        Write-Host ""
        Write-Host "3. postcss (<8.4.31)" -ForegroundColor Red
        Write-Host "   - Tipo: PostCSS line return parsing error" -ForegroundColor White
        Write-Host "   - Severidade: Moderada" -ForegroundColor White
        Write-Host ""
        Write-Host "4. webpack-dev-server (<=5.2.0)" -ForegroundColor Red
        Write-Host "   - Tipo: Source code theft vulnerability" -ForegroundColor White
        Write-Host "   - Severidade: Moderada" -ForegroundColor White
        Write-Host ""
        
        Write-Host "🔧 COMANDOS MANUAIS DE CORREÇÃO:" -ForegroundColor Green
        Write-Host "npm install brace-expansion@latest" -ForegroundColor Cyan
        Write-Host "npm install nth-check@latest" -ForegroundColor Cyan
        Write-Host "npm install postcss@latest" -ForegroundColor Cyan
        Write-Host "npm install webpack-dev-server@latest" -ForegroundColor Cyan
        Write-Host ""
        
        $manual = Read-Host "Executar atualizações manuais? (s/n)"
        if ($manual -eq "s" -or $manual -eq "S" -or $manual -eq "sim") {
            Write-Host "📦 Atualizando dependências..." -ForegroundColor Blue
            
            # Atualizar dependências específicas
            npm update brace-expansion
            npm update nth-check
            npm update postcss
            npm update webpack-dev-server
            
            Write-Host "📊 Verificando resultado..." -ForegroundColor Blue
            npm audit
        }
    }
    
    "4" {
        Write-Host "⚠️ Vulnerabilidades não corrigidas. Não recomendado para produção!" -ForegroundColor Red
    }
    
    default {
        Write-Host "❌ Opção inválida." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Blue
Write-Host "1. Teste a aplicação: npm start" -ForegroundColor White
Write-Host "2. Execute build de produção: npm run build:secure" -ForegroundColor White
Write-Host "3. Verifique novamente: npm audit" -ForegroundColor White
Write-Host ""

# Voltar ao diretório raiz
Set-Location ".."

Write-Host "📍 LOCALIZAÇÃO DOS SCRIPTS:" -ForegroundColor Yellow
Write-Host "- verify-deploy.ps1: $(Get-Location)\verify-deploy.ps1" -ForegroundColor Cyan
Write-Host "- deploy-godaddy.ps1: $(Get-Location)\deploy-godaddy.ps1" -ForegroundColor Cyan
Write-Host "- production-config.ps1: $(Get-Location)\production-config.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 DICA: Execute os scripts do diretório raiz (c:\Nautilus Aut\back)" -ForegroundColor Green

# Pausar para o usuário ler
Read-Host "Pressione Enter para finalizar"