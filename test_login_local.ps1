# Script para testar login local

# Função para testar endpoint específico
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [hashtable]$Headers = @{"Content-Type" = "application/json"}
    )
    
    try {
        Write-Host "\n=== Testando: $Method $Url ==="
        
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            TimeoutSec = 30
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json)
            Write-Host "Body: $($params.Body)"
        }
        
        $response = Invoke-WebRequest @params
        
        Write-Host "Status: $($response.StatusCode)"
        Write-Host "Response: $($response.Content)"
        
        return $true
    }
    catch {
        Write-Host "Erro: $($_.Exception.Message)"
        
        if ($_.Exception.Response) {
            Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
            
            try {
                $errorStream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($errorStream)
                $errorContent = $reader.ReadToEnd()
                Write-Host "Error Content: $errorContent"
            }
            catch {
                Write-Host "Não foi possível ler o conteúdo do erro"
            }
        }
        
        return $false
    }
}

# Testar servidor local
Write-Host "Testando servidor local na porta 5001..."

# 1. Test models
Test-Endpoint -Url "http://localhost:5001/test-models"

# 2. Login com credenciais corretas
$loginData = @{
    email = "admin@bigwhale.com"
    password = "Raikamaster1@"
}

Test-Endpoint -Url "http://localhost:5001/test-login-simple" -Method "POST" -Body $loginData

# 3. Testar com a segunda credencial
$loginData2 = @{
    email = "willian@lexxusadm.com.br"
    password = "Bigwhale202021@"
}

Test-Endpoint -Url "http://localhost:5001/test-login-simple" -Method "POST" -Body $loginData2

Write-Host "`nTestes locais concluidos."