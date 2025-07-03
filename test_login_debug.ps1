# Script para testar login com debug detalhado

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

# Testar conectividade básica
Write-Host "Iniciando testes de debug do backend..."

# 1. Health check
Test-Endpoint -Url "https://bigwhale-backend.onrender.com/api/health"

# 2. Test endpoint
Test-Endpoint -Url "https://bigwhale-backend.onrender.com/api/test"

# 3. Login com credenciais corretas
$loginData = @{
    email = "admin@bigwhale.com"
    password = "Raikamaster1@"
}

Test-Endpoint -Url "https://bigwhale-backend.onrender.com/api/auth/login" -Method "POST" -Body $loginData

# 4. Testar com a segunda credencial
$loginData2 = @{
    email = "willian@lexxusadm.com.br"
    password = "Bigwhale202021@"
}

Test-Endpoint -Url "https://bigwhale-backend.onrender.com/api/auth/login" -Method "POST" -Body $loginData2

Write-Host "`nTestes concluidos."