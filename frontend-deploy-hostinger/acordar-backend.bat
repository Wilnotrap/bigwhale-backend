@echo off
echo ========================================
echo    SCRIPT PARA ACORDAR BACKEND RENDER
echo ========================================
echo.
echo Testando conectividade com o backend...
echo.

echo [1/4] Testando endpoint de health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://bigwhale-backend.onrender.com/api/health' -Method GET -TimeoutSec 60; Write-Host 'Status:' $response.StatusCode; Write-Host 'Resposta:' $response.Content } catch { Write-Host 'Erro:' $_.Exception.Message }"
echo.

echo [2/4] Aguardando 10 segundos...
timeout /t 10 /nobreak > nul
echo.

echo [3/4] Testando endpoint de teste...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://bigwhale-backend.onrender.com/api/test' -Method GET -TimeoutSec 30; Write-Host 'Status:' $response.StatusCode; Write-Host 'Resposta:' $response.Content } catch { Write-Host 'Erro:' $_.Exception.Message }"
echo.

echo [4/4] Testando login de admin...
powershell -Command "try { $body = @{ email='admin@bigwhale.com'; password='Raikamaster1@' } | ConvertTo-Json; $response = Invoke-WebRequest -Uri 'https://bigwhale-backend.onrender.com/api/auth/login' -Method POST -Body $body -ContentType 'application/json' -TimeoutSec 30; Write-Host 'Status:' $response.StatusCode; if($response.StatusCode -eq 200) { Write-Host 'LOGIN FUNCIONANDO!' } else { Write-Host 'Login falhou' } } catch { Write-Host 'Erro no login:' $_.Exception.Message }"
echo.

echo ========================================
echo Se todos os testes passaram, o backend
echo esta funcionando e voce pode tentar
echo fazer login no frontend novamente.
echo ========================================
echo.
pause