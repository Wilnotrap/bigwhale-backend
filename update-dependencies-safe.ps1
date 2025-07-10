# 🔄 Script de Atualização Segura de Dependências
# Nautilus Automação - Safe Dependencies Update

Write-Host "🔄 Atualização Segura de Dependências - Nautilus Automação" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Yellow

# Navegar para o diretório do frontend
Set-Location "./frontend"

Write-Host "📍 Diretório atual: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Backup do package.json atual
Write-Host "💾 Criando backup do package.json..." -ForegroundColor Blue
Copy-Item "package.json" "package.json.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host "   ✅ Backup criado" -ForegroundColor Green
Write-Host ""

# Verificar vulnerabilidades atuais
Write-Host "🔍 Verificando vulnerabilidades atuais..." -ForegroundColor Blue
try {
    $auditResult = npm audit --json 2>$null | ConvertFrom-Json
    $vulnerabilities = $auditResult.metadata.vulnerabilities
    
    Write-Host "📊 Vulnerabilidades encontradas:" -ForegroundColor Yellow
    Write-Host "   - Baixa: $($vulnerabilities.low)" -ForegroundColor Green
    Write-Host "   - Moderada: $($vulnerabilities.moderate)" -ForegroundColor Yellow
    Write-Host "   - Alta: $($vulnerabilities.high)" -ForegroundColor Red
    Write-Host "   - Crítica: $($vulnerabilities.critical)" -ForegroundColor Magenta
} catch {
    Write-Host "⚠️ Não foi possível obter detalhes das vulnerabilidades" -ForegroundColor Yellow
    npm audit
}

Write-Host ""

# Função para atualizar dependência específica
function Update-Dependency($package, $version = "latest") {
    Write-Host "📦 Atualizando $package para $version..." -ForegroundColor Blue
    
    try {
        if ($version -eq "latest") {
            npm install $package@latest
        } else {
            npm install $package@$version
        }
        Write-Host "   ✅ $package atualizado com sucesso" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   ❌ Erro ao atualizar $package" -ForegroundColor Red
        return $false
    }
}

# Função para testar build após atualização
function Test-Build {
    Write-Host "🧪 Testando build..." -ForegroundColor Blue
    
    try {
        $buildResult = npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Build bem-sucedido" -ForegroundColor Green
            return $true
        } else {
            Write-Host "   ❌ Build falhou" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "   ❌ Erro durante o build" -ForegroundColor Red
        return $false
    }
}

# Estratégia de atualização segura
Write-Host "🛠️ ESTRATÉGIA DE ATUALIZAÇÃO SEGURA" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""

# 1. Correção automática primeiro
Write-Host "1️⃣ Tentando correção automática..." -ForegroundColor Blue
npm audit fix

# Verificar se ainda há vulnerabilidades
Write-Host "🔍 Verificando vulnerabilidades restantes..." -ForegroundColor Blue
$auditCheck = npm audit --audit-level moderate 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Todas as vulnerabilidades foram corrigidas!" -ForegroundColor Green
    Write-Host "📋 Executando teste final..." -ForegroundColor Blue
    
    if (Test-Build) {
        Write-Host "🎉 Atualização concluída com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Build falhou após correções. Verifique os logs." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Ainda existem vulnerabilidades. Tentando correções específicas..." -ForegroundColor Yellow
    Write-Host ""
    
    # 2. Atualizações específicas para vulnerabilidades conhecidas
    Write-Host "2️⃣ Aplicando correções específicas..." -ForegroundColor Blue
    
    # Lista de dependências problemáticas e suas versões seguras
    $secureVersions = @{
        "nth-check" = "2.0.1"
        "postcss" = "8.4.31"
        "brace-expansion" = "2.0.1"
    }
    
    $updateSuccess = $true
    
    foreach ($package in $secureVersions.Keys) {
        $version = $secureVersions[$package]
        Write-Host "📦 Verificando $package..." -ForegroundColor Cyan
        
        # Verificar se o pacote está instalado
        $packageInfo = npm list $package --depth=0 2>$null
        if ($packageInfo -match $package) {
            Write-Host "   Atualizando para versão segura: $version" -ForegroundColor Yellow
            $result = Update-Dependency $package $version
            if (-not $result) {
                $updateSuccess = $false
            }
        } else {
            Write-Host "   Pacote não encontrado diretamente (pode ser dependência transitiva)" -ForegroundColor Gray
        }
    }
    
    # 3. Teste após atualizações específicas
    Write-Host ""
    Write-Host "3️⃣ Testando após atualizações específicas..." -ForegroundColor Blue
    
    if (Test-Build) {
        Write-Host "✅ Build bem-sucedido após atualizações específicas" -ForegroundColor Green
        
        # Verificar vulnerabilidades novamente
        Write-Host "🔍 Verificação final de vulnerabilidades..." -ForegroundColor Blue
        npm audit
        
    } else {
        Write-Host "❌ Build falhou. Restaurando backup..." -ForegroundColor Red
        
        # Restaurar backup
        $backupFile = Get-ChildItem "package.json.backup.*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($backupFile) {
            Copy-Item $backupFile.FullName "package.json"
            Write-Host "📦 Reinstalando dependências do backup..." -ForegroundColor Yellow
            npm install
            Write-Host "✅ Backup restaurado" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS RECOMENDADOS:" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue
Write-Host ""
Write-Host "1. Teste a aplicação localmente:" -ForegroundColor White
Write-Host "   npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Execute os testes:" -ForegroundColor White
Write-Host "   npm test" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Build de produção:" -ForegroundColor White
Write-Host "   npm run build:secure" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Auditoria final:" -ForegroundColor White
Write-Host "   npm audit" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Se tudo estiver OK, execute o deploy:" -ForegroundColor White
Write-Host "   cd .." -ForegroundColor Cyan
Write-Host "   .\deploy-godaddy.ps1" -ForegroundColor Cyan
Write-Host ""

# Voltar ao diretório raiz
Set-Location ".."

Write-Host "📍 LOCALIZAÇÃO DOS SCRIPTS DE DEPLOY:" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Yellow
Write-Host "Você está agora em: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Scripts disponíveis:" -ForegroundColor White
Write-Host "- .\verify-deploy.ps1 (verificação pós-deploy)" -ForegroundColor Cyan
Write-Host "- .\deploy-godaddy.ps1 (deploy automatizado)" -ForegroundColor Cyan
Write-Host "- .\production-config.ps1 (configuração de produção)" -ForegroundColor Cyan
Write-Host "- .\fix-security-vulnerabilities.ps1 (correção de vulnerabilidades)" -ForegroundColor Cyan
Write-Host ""

Write-Host "💡 DICA: O erro anterior com verify-deploy.ps1 ocorreu porque você estava" -ForegroundColor Green
Write-Host "    no diretório 'frontend'. Agora você está no diretório correto!" -ForegroundColor Green
Write-Host ""

# Pausar para o usuário ler
Read-Host "Pressione Enter para finalizar"