@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 🚀 BITGET TRADING - EXECUÇÃO DIRETA
echo ========================================
echo.

echo 📁 Diretório atual: %CD%
echo 🔍 Verificando arquivos...

if not exist ".venv\Scripts\python.exe" (
    echo ❌ Python do ambiente virtual não encontrado!
    echo 📍 Esperado em: %CD%\.venv\Scripts\python.exe
    pause
    exit /b 1
)

if not exist "backend\start_server_simple.py" (
    echo ❌ Arquivo do servidor não encontrado!
    echo 📍 Esperado em: %CD%\backend\start_server_simple.py
    pause
    exit /b 1
)

echo ✅ Ambiente virtual encontrado
echo ✅ Servidor encontrado
echo.
echo 🔄 Iniciando servidor Flask...
echo 🌐 URL: http://localhost:5000
echo 📊 Health: http://localhost:5000/health
echo.
echo ⚠️  Para parar o servidor, feche esta janela ou pressione Ctrl+C
echo ========================================
echo.

REM Executar o servidor
".venv\Scripts\python.exe" "backend\start_server_simple.py"

echo.
echo ========================================
echo 🛑 Servidor finalizado
echo ========================================
pause