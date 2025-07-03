@echo off
echo ========================================
echo    INICIALIZANDO SISTEMA BITGET
echo ========================================
echo.

echo [1/4] Navegando para o diretorio backend...
cd /d "%~dp0backend"
if errorlevel 1 (
    echo ERRO: Nao foi possivel acessar o diretorio backend
    pause
    exit /b 1
)

echo [2/4] Corrigindo banco de dados...
python fix_sistema.py
if errorlevel 1 (
    echo ERRO: Falha ao corrigir o banco de dados
    echo Tente executar manualmente: python fix_sistema.py
    pause
    exit /b 1
)

echo.
echo [3/4] Iniciando backend...
echo Backend sera iniciado em uma nova janela...
start "Backend Bitget" cmd /k "python app.py"

echo.
echo [4/4] Aguardando 5 segundos para o backend inicializar...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo       SISTEMA INICIALIZADO!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: Execute 'npm start' na pasta frontend
echo.
echo CREDENCIAIS DE TESTE:
echo - admin@teste.com / 123456 (Admin)
echo - user@teste.com / 123456 (Usuario)
echo - teste@teste.com / 123456 (Teste)
echo.
echo Pressione qualquer tecla para continuar...
pause >nul