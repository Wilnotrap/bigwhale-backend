# Teste de conectividade com o backend
try {
    Write-Host "Testando conectividade com o backend..."
    $response = Invoke-WebRequest -Uri "https://bigwhale-backend.onrender.com/api/health" -Method GET -TimeoutSec 30
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Content: $($response.Content)"
} catch {
    Write-Host "Erro ao conectar com o backend: $($_.Exception.Message)"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
}

# Teste do endpoint de login
try {
    Write-Host "`nTestando endpoint de login..."
    $loginData = @{
        email = "admin@bigwhale.com"
        password = "Raikamaster1@"
    } | ConvertTo-Json
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "https://bigwhale-backend.onrender.com/api/auth/login" -Method POST -Body $loginData -Headers $headers -TimeoutSec 30
    Write-Host "Login Status Code: $($response.StatusCode)"
    Write-Host "Login Response: $($response.Content)"
} catch {
    Write-Host "Erro no login: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Login Status Code: $($_.Exception.Response.StatusCode.value__)"
        $errorStream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorStream)
        $errorContent = $reader.ReadToEnd()
        Write-Host "Error Content: $errorContent"
    }
}

Write-Host "`nTeste concluído."