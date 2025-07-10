# 🧪 SCRIPT DE TESTE - DEPLOY RENDER
# Teste para verificar se o deploy no Render está funcionando

Write-Host "🧪 TESTE DE DEPLOY NO RENDER - BIGWHALE" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Configurações
$RENDER_URL = "https://bigwhale-backend.onrender.com"
$HEALTH_ENDPOINT = "$RENDER_URL/api/health"
$LOGIN_ENDPOINT = "$RENDER_URL/api/auth/login"

# Função para testar endpoint
function Test-Endpoint {
    param($Url, $Method = "GET", $Body = $null)
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = 30
            ContentType = "application/json"
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-RestMethod @params
        return @{
            Success = $true
            Response = $response
            StatusCode = 200
        }
    }
    catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
            StatusCode = $_.Exception.Response.StatusCode.value__
        }
    }
}

# 1. TESTE DE HEALTH CHECK
Write-Host "🔍 1. Testando Health Check..." -ForegroundColor Yellow
Write-Host "   URL: $HEALTH_ENDPOINT" -ForegroundColor Cyan

$healthResult = Test-Endpoint -Url $HEALTH_ENDPOINT

if ($healthResult.Success) {
    Write-Host "   ✅ Health Check passou!" -ForegroundColor Green
    Write-Host "   📊 Status: $($healthResult.Response.status)" -ForegroundColor Cyan
    Write-Host "   🌐 Ambiente: $($healthResult.Response.environment)" -ForegroundColor Cyan
    Write-Host "   📅 Timestamp: $($healthResult.Response.timestamp)" -ForegroundColor Cyan
    Write-Host "   💬 Mensagem: $($healthResult.Response.message)" -ForegroundColor Cyan
} else {
    Write-Host "   ❌ Health Check falhou!" -ForegroundColor Red
    Write-Host "   🚨 Erro: $($healthResult.Error)" -ForegroundColor Red
    Write-Host "   📊 Status Code: $($healthResult.StatusCode)" -ForegroundColor Red
}

Write-Host ""

# 2. TESTE DE LOGIN
Write-Host "🔍 2. Testando Login..." -ForegroundColor Yellow
Write-Host "   URL: $LOGIN_ENDPOINT" -ForegroundColor Cyan

$loginBody = @{
    email = "admin@bigwhale.com"
    password = "Raikamaster1@"
} | ConvertTo-Json

$loginResult = Test-Endpoint -Url $LOGIN_ENDPOINT -Method "POST" -Body $loginBody

if ($loginResult.Success) {
    Write-Host "   ✅ Login passou!" -ForegroundColor Green
    Write-Host "   👤 Usuário: $($loginResult.Response.user.email)" -ForegroundColor Cyan
    Write-Host "   🔑 Admin: $($loginResult.Response.user.is_admin)" -ForegroundColor Cyan
    Write-Host "   ✅ Ativo: $($loginResult.Response.user.is_active)" -ForegroundColor Cyan
} else {
    Write-Host "   ❌ Login falhou!" -ForegroundColor Red
    Write-Host "   🚨 Erro: $($loginResult.Error)" -ForegroundColor Red
    Write-Host "   📊 Status Code: $($loginResult.StatusCode)" -ForegroundColor Red
}

Write-Host ""

# 3. TESTE DE CONECTIVIDADE FRONTEND
Write-Host "🔍 3. Testando conectividade com Frontend..." -ForegroundColor Yellow

# Criar arquivo de teste HTML
$testHtml = @"
<!DOCTYPE html>
<html>
<head>
    <title>Teste de Conectividade - BigWhale</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .error { color: red; }
        .info { color: blue; }
        .test-result { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>🧪 Teste de Conectividade - BigWhale</h1>
    <div id="results"></div>
    
    <script>
        const RENDER_URL = '$RENDER_URL';
        const resultsDiv = document.getElementById('results');
        
        function addResult(title, message, type = 'info') {
            const div = document.createElement('div');
            div.className = 'test-result ' + type;
            div.innerHTML = '<strong>' + title + ':</strong> ' + message;
            resultsDiv.appendChild(div);
        }
        
        async function testHealth() {
            try {
                const response = await fetch(RENDER_URL + '/api/health');
                const data = await response.json();
                
                if (data.status === 'healthy') {
                    addResult('✅ Health Check', 'Backend está funcionando: ' + data.message, 'success');
                } else {
                    addResult('⚠️ Health Check', 'Status: ' + data.status, 'error');
                }
            } catch (error) {
                addResult('❌ Health Check', 'Erro: ' + error.message, 'error');
            }
        }
        
        async function testLogin() {
            try {
                const response = await fetch(RENDER_URL + '/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: 'admin@bigwhale.com',
                        password: 'Raikamaster1@'
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    addResult('✅ Login', 'Login funcionando para: ' + data.user.email, 'success');
                } else {
                    addResult('❌ Login', 'Erro: ' + data.message, 'error');
                }
            } catch (error) {
                addResult('❌ Login', 'Erro: ' + error.message, 'error');
            }
        }
        
        // Executar testes
        addResult('🔍 Iniciando testes', 'Testando conectividade com ' + RENDER_URL, 'info');
        testHealth();
        setTimeout(testLogin, 1000);
    </script>
</body>
</html>
"@

$testHtml | Out-File -FilePath "test_render_connectivity.html" -Encoding UTF8
Write-Host "   ✅ Arquivo de teste HTML criado: test_render_connectivity.html" -ForegroundColor Green

# RESUMO FINAL
Write-Host ""
Write-Host "📊 RESUMO DO TESTE:" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

if ($healthResult.Success) {
    Write-Host "✅ Health Check: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Health Check: FALHOU" -ForegroundColor Red
}

if ($loginResult.Success) {
    Write-Host "✅ Login: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Login: FALHOU" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔧 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Se todos os testes passaram: Deploy está funcionando!" -ForegroundColor White
Write-Host "2. Se algum teste falhou: Verificar logs do Render" -ForegroundColor White
Write-Host "3. Abrir test_render_connectivity.html no navegador para teste visual" -ForegroundColor White
Write-Host "4. Configurar frontend na Hostinger para usar a URL do Render" -ForegroundColor White
Write-Host ""
Write-Host "💡 DICA: Se o backend estiver 'dormindo', pode demorar ~30s para responder na primeira chamada" -ForegroundColor Yellow
Write-Host "" 