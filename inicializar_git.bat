@echo off
echo ========================================
echo INICIALIZANDO REPOSITORIO GIT
echo ========================================

echo.
echo 1. Inicializando repositorio Git...
git init

echo.
echo 2. Adicionando todos os arquivos...
git add .

echo.
echo 3. Fazendo commit inicial...
git commit -m "Deploy inicial BigWhale Backend - Render"

echo.
echo 4. Configurando branch principal...
git branch -M main

echo.
echo ========================================
echo REPOSITORIO INICIALIZADO COM SUCESSO!
echo ========================================
echo.
echo PROXIMOS PASSOS:
echo 1. Crie um repositorio no GitHub
echo 2. Execute: git remote add origin URL_DO_SEU_REPO
echo 3. Execute: git push -u origin main
echo.
echo CONFIGURACAO DO RENDER:
echo - Build Command: pip install -r requirements.txt
echo - Start Command: cd backend ^&^& gunicorn app:application --bind 0.0.0.0:$PORT
echo - Environment: Python 3.11
echo.
echo VARIAVEIS DE AMBIENTE NECESSARIAS:
echo - FLASK_SECRET_KEY (gerar automaticamente)
echo - AES_ENCRYPTION_KEY (gerar automaticamente)  
echo - DATABASE_URL (PostgreSQL do Render)
echo.
pause