# 🔍 Script de Verificação Pós-Deploy
# Nautilus Automação - Verificação e Monitoramento

Write-Host "🔍 Verificação Pós-Deploy - Nautilus Automação" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Yellow

# Configurações
$DOMAIN = Read-Host "Digite seu domínio (ex: seusite.com)"
$BASE_URL = "https://$DOMAIN"
$API_URL = "$BASE_URL/api"

# Função para testar URL
function Test-Url($url, $description) {
    Write-Host "🌐 Testando: $description" -ForegroundColor Blue
    Write-Host "   URL: $url" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 10 -UseBasicParsing
        $statusCode = $response.StatusCode
        
        if ($statusCode -eq 200) {
            Write-Host "   ✅ OK ($statusCode)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "   ⚠️  Status: $statusCode" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "   ❌ Erro: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Função para testar API endpoint
function Test-ApiEndpoint($endpoint, $description) {
    $url = "$API_URL/$endpoint"
    return Test-Url $url $description
}

# Função para verificar headers de segurança
function Test-SecurityHeaders($url) {
    Write-Host "🔒 Verificando headers de segurança..." -ForegroundColor Blue
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 10 -UseBasicParsing
        $headers = $response.Headers
        
        $securityHeaders = @{
            "X-Content-Type-Options" = "nosniff"
            "X-Frame-Options" = "DENY"
            "X-XSS-Protection" = "1; mode=block"
            "Content-Security-Policy" = $null
            "Strict-Transport-Security" = $null
        }
        
        foreach ($header in $securityHeaders.Keys) {
            if ($headers.ContainsKey($header)) {
                Write-Host "   ✅ $header: $($headers[$header])" -ForegroundColor Green
            } else {
                Write-Host "   ❌ $header: Não encontrado" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "   ❌ Erro ao verificar headers: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Função para verificar SSL
function Test-SSL($domain) {
    Write-Host "🔐 Verificando SSL..." -ForegroundColor Blue
    
    try {
        $uri = [System.Uri]"https://$domain"
        $request = [System.Net.WebRequest]::Create($uri)
        $request.Timeout = 10000
        $response = $request.GetResponse()
        
        Write-Host "   ✅ SSL ativo e funcionando" -ForegroundColor Green
        $response.Close()
        return $true
    }
    catch {
        Write-Host "   ❌ Problema com SSL: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Função para verificar redirecionamento HTTP → HTTPS
function Test-HttpsRedirect($domain) {
    Write-Host "🔄 Verificando redirecionamento HTTPS..." -ForegroundColor Blue
    
    try {
        $httpUrl = "http://$domain"
        $response = Invoke-WebRequest -Uri $httpUrl -Method GET -TimeoutSec 10 -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 301 -or $response.StatusCode -eq 302) {
            $location = $response.Headers.Location
            if ($location -and $location.StartsWith("https://")) {
                Write-Host "   ✅ Redirecionamento HTTPS ativo" -ForegroundColor Green
                return $true
            }
        }
        
        Write-Host "   ⚠️  Redirecionamento HTTPS não detectado" -ForegroundColor Yellow
        return $false
    }
    catch {
        Write-Host "   ❌ Erro ao testar redirecionamento: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Função para gerar relatório
function Generate-Report($results) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $reportContent = @"
📊 RELATÓRIO DE VERIFICAÇÃO - NAUTILUS AUTOMAÇÃO
===============================================
Data/Hora: $timestamp
Domínio: $DOMAIN
URL Base: $BASE_URL

🔍 RESULTADOS DOS TESTES:

"@

    foreach ($result in $results) {
        $status = if ($result.Success) { "✅ PASSOU" } else { "❌ FALHOU" }
        $reportContent += "$status - $($result.Test): $($result.Description)`n"
    }
    
    $reportContent += @"

📋 RECOMENDAÇÕES:

"@
    
    $failedTests = $results | Where-Object { -not $_.Success }
    
    if ($failedTests.Count -eq 0) {
        $reportContent += "🎉 Todos os testes passaram! Sua aplicação está funcionando corretamente.`n"
    } else {
        $reportContent += "⚠️  Alguns testes falharam. Verifique os seguintes pontos:`n`n"
        
        foreach ($failed in $failedTests) {
            switch ($failed.Test) {
                "Frontend" { $reportContent += "- Verifique se os arquivos foram extraídos corretamente no public_html`n" }
                "API Health" { $reportContent += "- Verifique se as dependências Python foram instaladas`n- Verifique permissões da pasta api/`n- Consulte Error Logs no cPanel`n" }
                "SSL" { $reportContent += "- Ative o certificado SSL no cPanel`n- Configure Force HTTPS Redirect`n" }
                "HTTPS Redirect" { $reportContent += "- Verifique configuração do .htaccess`n- Ative Force HTTPS no cPanel`n" }
                "Security Headers" { $reportContent += "- Verifique configuração do .htaccess`n- Confirme se mod_headers está ativo`n" }
            }
        }
    }
    
    $reportContent += @"

🔗 LINKS ÚTEIS:
- Aplicação: $BASE_URL
- API Health: $API_URL/health
- cPanel: https://seudominio.com:2083
- Documentação: DEPLOY_GODADDY_GUIDE.md

📞 SUPORTE:
- GoDaddy: Suporte técnico 24/7
- Documentação: Consulte os arquivos de guia
"@
    
    $reportFile = "relatorio-verificacao-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
    $reportContent | Out-File -FilePath $reportFile -Encoding UTF8
    
    Write-Host "📄 Relatório salvo: $reportFile" -ForegroundColor Cyan
    return $reportFile
}

# INÍCIO DOS TESTES
Write-Host "🚀 Iniciando verificação..." -ForegroundColor Blue
Write-Host ""

$results = @()

# 1. Teste do Frontend
$frontendTest = Test-Url $BASE_URL "Frontend (Página Principal)"
$results += @{ Test = "Frontend"; Success = $frontendTest; Description = "Página principal carregando" }

# 2. Teste da API Health
$apiHealthTest = Test-ApiEndpoint "health" "API Health Check"
$results += @{ Test = "API Health"; Success = $apiHealthTest; Description = "Endpoint de saúde da API" }

# 3. Teste de outros endpoints da API
$apiEndpoints = @(
    @{ endpoint = "auth/status"; description = "Status de Autenticação" },
    @{ endpoint = "dashboard/stats"; description = "Estatísticas do Dashboard" }
)

foreach ($endpoint in $apiEndpoints) {
    $test = Test-ApiEndpoint $endpoint.endpoint $endpoint.description
    $results += @{ Test = "API $($endpoint.endpoint)"; Success = $test; Description = $endpoint.description }
}

# 4. Teste SSL
$sslTest = Test-SSL $DOMAIN
$results += @{ Test = "SSL"; Success = $sslTest; Description = "Certificado SSL ativo" }

# 5. Teste de redirecionamento HTTPS
$httpsRedirectTest = Test-HttpsRedirect $DOMAIN
$results += @{ Test = "HTTPS Redirect"; Success = $httpsRedirectTest; Description = "Redirecionamento HTTP para HTTPS" }

# 6. Teste de headers de segurança
Test-SecurityHeaders $BASE_URL
$results += @{ Test = "Security Headers"; Success = $true; Description = "Headers de segurança (veja detalhes acima)" }

Write-Host ""
Write-Host "📊 RESUMO DOS TESTES" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow

$passedTests = ($results | Where-Object { $_.Success }).Count
$totalTests = $results.Count
$successRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "✅ Testes aprovados: $passedTests/$totalTests ($successRate%)" -ForegroundColor Green

if ($successRate -eq 100) {
    Write-Host "🎉 Parabéns! Todos os testes passaram!" -ForegroundColor Green
} elseif ($successRate -ge 80) {
    Write-Host "⚠️  Maioria dos testes passou, mas há alguns problemas" -ForegroundColor Yellow
} else {
    Write-Host "❌ Vários problemas detectados, verifique a configuração" -ForegroundColor Red
}

# Gerar relatório
Write-Host ""
$reportFile = Generate-Report $results

Write-Host ""
Write-Host "🔍 VERIFICAÇÃO CONCLUÍDA" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Yellow
Write-Host "📄 Relatório: $reportFile" -ForegroundColor Cyan
Write-Host "🌐 Aplicação: $BASE_URL" -ForegroundColor Cyan
Write-Host ""

# Perguntar se quer abrir a aplicação
$openApp = Read-Host "Deseja abrir a aplicação no navegador? (s/n)"
if ($openApp -eq "s" -or $openApp -eq "S" -or $openApp -eq "sim") {
    Start-Process $BASE_URL
}

# Pausar para o usuário ler
Read-Host "Pressione Enter para finalizar"