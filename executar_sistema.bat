@echo off
echo ========================================
echo    EXECUTANDO SISTEMA BITGET
echo ========================================
echo.

echo [1/3] Iniciando Backend...
echo Navegando para backend...
cd /d "%~dp0backend"

echo Corrigindo banco de dados...
python fix_sistema.py
if errorlevel 1 (
    echo AVISO: Erro ao corrigir banco, continuando...
)

echo Iniciando servidor Flask...
start "Backend Bitget" cmd /k "python app.py"

echo.
echo [2/3] Aguardando backend inicializar...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Iniciando Frontend...
echo Navegando para frontend...
cd /d "%~dp0frontend"

echo Instalando dependencias se necessario...
if not exist node_modules (
    echo Instalando dependencias do npm...
    npm install
)

echo Iniciando servidor React...
start "Frontend Bitget" cmd /k "npm start"

echo.
echo ========================================
echo       SISTEMA INICIADO!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo CREDENCIAIS DE TESTE:
echo - admin@teste.com / 123456 (Admin)
echo - user@teste.com / 123456 (Usuario)
echo - teste@teste.com / 123456 (Teste)
echo.
echo Pressione qualquer tecla para fechar...
pause >nul