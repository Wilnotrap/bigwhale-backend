# ========================================
# 🧪 BigWhale Deploy Test Script
# ========================================

Write-Host "🧪 BigWhale Deploy Test Script" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Configurações
$BACKEND_URL = "https://bigwhale-backend.onrender.com"
$FRONTEND_URL = "https://bwhale.site"
$TIMEOUT = 10

# Função para testar URL
function Test-URL {
    param(
        [string]$Url,
        [string]$Description,
        [int]$TimeoutSec = 10
    )
    
    Write-Host "🔍 Testando ${Description}..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $TimeoutSec -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ ${Description}: OK (Status: $($response.StatusCode))" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ ${Description}: Status $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ ${Description}: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Função para testar API JSON
function Test-API {
    param(
        [string]$Url,
        [string]$Description,
        [int]$TimeoutSec = 10
    )
    
    Write-Host "🔍 Testando ${Description}..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri $Url -Method GET -TimeoutSec $TimeoutSec
        if ($response -and $response.status) {
            Write-Host "✅ ${Description}: $($response.status)" -ForegroundColor Green
            if ($response.message) {
                Write-Host "   📝 Mensagem: $($response.message)" -ForegroundColor Cyan
            }
            return $true
        } else {
            Write-Host "⚠️ ${Description}: Resposta inválida" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ ${Description}: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Função para testar recursos específicos
function Test-Resource {
    param(
        [string]$Url,
        [string]$Description,
        [string]$ExpectedContent = $null
    )
    
    Write-Host "🔍 Testando ${Description}..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $TIMEOUT -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            if ($ExpectedContent -and $response.Content -match $ExpectedContent) {
                Write-Host "✅ ${Description}: OK (Conteúdo encontrado)" -ForegroundColor Green
                return $true
            } elseif (-not $ExpectedContent) {
                Write-Host "✅ ${Description}: OK" -ForegroundColor Green
                return $true
            } else {
                Write-Host "⚠️ ${Description}: Conteúdo esperado não encontrado" -ForegroundColor Yellow
                return $false
            }
        } else {
            Write-Host "⚠️ ${Description}: Status $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ ${Description}: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Iniciar testes
Write-Host "🚀 Iniciando testes do deploy..." -ForegroundColor Cyan
Write-Host ""

# Contadores
$totalTests = 0
$passedTests = 0

# 1. Testar Backend
Write-Host "🔧 BACKEND TESTS" -ForegroundColor Magenta
Write-Host "------------------------" -ForegroundColor Magenta

$totalTests++
if (Test-URL -Url $BACKEND_URL -Description "Backend Base URL") {
    $passedTests++
}

$totalTests++
if (Test-API -Url "$BACKEND_URL/api/health" -Description "Health Check") {
    $passedTests++
}

$totalTests++
if (Test-URL -Url "$BACKEND_URL/api/test" -Description "Test Endpoint") {
    $passedTests++
}

Write-Host ""

# 2. Testar Frontend
Write-Host "🎨 FRONTEND TESTS" -ForegroundColor Magenta
Write-Host "------------------------" -ForegroundColor Magenta

$totalTests++
if (Test-URL -Url $FRONTEND_URL -Description "Frontend Base URL") {
    $passedTests++
}

$totalTests++
if (Test-Resource -Url $FRONTEND_URL -Description "Frontend HTML" -ExpectedContent "Nautilus Automação") {
    $passedTests++
}

Write-Host ""

# 3. Testar Recursos Específicos
Write-Host "📦 RESOURCE TESTS" -ForegroundColor Magenta
Write-Host "------------------------" -ForegroundColor Magenta

# Testar se Google Fonts estão carregando
$totalTests++
if (Test-URL -Url "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" -Description "Google Fonts") {
    $passedTests++
}

# Testar favicon
$totalTests++
if (Test-URL -Url "$FRONTEND_URL/favicon.ico" -Description "Favicon") {
    $passedTests++
}

# Testar manifest
$totalTests++
if (Test-URL -Url "$FRONTEND_URL/manifest.json" -Description "Manifest") {
    $passedTests++
}

Write-Host ""

# 4. Testar Conectividade CORS
Write-Host "🔗 CORS TESTS" -ForegroundColor Magenta
Write-Host "------------------------" -ForegroundColor Magenta

Write-Host "🔍 Testando CORS..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = $FRONTEND_URL
        "Access-Control-Request-Method" = "GET"
        "Access-Control-Request-Headers" = "Content-Type"
    }
    
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/health" -Method OPTIONS -Headers $headers -TimeoutSec $TIMEOUT -UseBasicParsing
    
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 204) {
        Write-Host "✅ CORS: OK" -ForegroundColor Green
        $totalTests++
        $passedTests++
    } else {
        Write-Host "⚠️ CORS: Status $($response.StatusCode)" -ForegroundColor Yellow
        $totalTests++
    }
} catch {
    Write-Host "❌ CORS: $($_.Exception.Message)" -ForegroundColor Red
    $totalTests++
}

Write-Host ""

# 5. Testar Segurança (Headers)
Write-Host "🔒 SECURITY TESTS" -ForegroundColor Magenta
Write-Host "------------------------" -ForegroundColor Magenta

Write-Host "🔍 Testando Headers de Segurança..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $FRONTEND_URL -Method GET -TimeoutSec $TIMEOUT -UseBasicParsing
    
    $securityHeaders = @{
        "X-Content-Type-Options" = "nosniff"
        "X-Frame-Options" = "DENY"
        "X-XSS-Protection" = "1; mode=block"
    }
    
    $headerTests = 0
    $headerPassed = 0
    
    foreach ($header in $securityHeaders.GetEnumerator()) {
        $headerTests++
        $totalTests++
        
        if ($response.Headers[$header.Key] -eq $header.Value) {
            Write-Host "  ✅ $($header.Key): OK" -ForegroundColor Green
            $headerPassed++
            $passedTests++
        } else {
            Write-Host "  ⚠️ $($header.Key): Não encontrado ou incorreto" -ForegroundColor Yellow
        }
    }
    
    Write-Host "📊 Headers de Segurança: $headerPassed/$headerTests" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Headers de Segurança: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Relatório Final
Write-Host "📊 RELATÓRIO FINAL" -ForegroundColor Magenta
Write-Host "=========================================" -ForegroundColor Magenta

$successRate = [math]::Round(($passedTests / $totalTests) * 100, 2)

Write-Host "✅ Testes Passados: $passedTests" -ForegroundColor Green
Write-Host "❌ Testes Falharam: $($totalTests - $passedTests)" -ForegroundColor Red
Write-Host "📈 Taxa de Sucesso: $successRate%" -ForegroundColor Cyan

if ($successRate -ge 80) {
    Write-Host "🎉 DEPLOY ESTÁ FUNCIONANDO CORRETAMENTE!" -ForegroundColor Green
} elseif ($successRate -ge 60) {
    Write-Host "⚠️ DEPLOY PARCIALMENTE FUNCIONANDO - Verificar problemas" -ForegroundColor Yellow
} else {
    Write-Host "❌ DEPLOY COM PROBLEMAS - Necessário correções" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 URLs para Teste Manual:" -ForegroundColor Cyan
Write-Host "   Frontend: $FRONTEND_URL" -ForegroundColor White
Write-Host "   Backend Health: $BACKEND_URL/api/health" -ForegroundColor White
Write-Host "   Login: admin@bigwhale.com / Raikamaster1@" -ForegroundColor White

Write-Host ""
Write-Host "📝 Próximos Passos:" -ForegroundColor Yellow
Write-Host "1. Testar login manual no site" -ForegroundColor White
Write-Host "2. Verificar console do navegador para erros" -ForegroundColor White
Write-Host "3. Testar funcionalidades principais" -ForegroundColor White

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 