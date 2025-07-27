#!/usr/bin/env pwsh
# Script para corrigir SSL e fazer redeploy no Render
# Versão: 2025-01-27

Write-Host "🔧 CORREÇÃO SSL POSTGRESQL + REDEPLOY RENDER" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# 1. Verificar se estamos no diretório correto
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Erro: app.py não encontrado. Execute este script na pasta backend-deploy-render" -ForegroundColor Red
    exit 1
}

# 2. Mostrar as correções aplicadas
Write-Host "✅ Correções SSL aplicadas:" -ForegroundColor Green
Write-Host "   - sslmode=require" -ForegroundColor Yellow
Write-Host "   - sslcert= sslkey= sslrootcert= (vazios para Render)" -ForegroundColor Yellow
Write-Host "   - connect_args com SSL configurado" -ForegroundColor Yellow
Write-Host ""

# 3. Verificar status do Git
Write-Host "📋 Status do repositório:" -ForegroundColor Blue
git status --porcelain

# 4. Adicionar mudanças
Write-Host "`n📤 Adicionando correções SSL..." -ForegroundColor Blue
git add app.py

# 5. Fazer commit
$commitMessage = "fix: Corrigir configuração SSL PostgreSQL para Render - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
Write-Host "💾 Fazendo commit: $commitMessage" -ForegroundColor Blue
git commit -m "$commitMessage"

# 6. Push para GitHub
Write-Host "`n🚀 Enviando para GitHub..." -ForegroundColor Blue
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ CORREÇÃO SSL ENVIADA COM SUCESSO!" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    
    Write-Host "`n📋 PRÓXIMOS PASSOS MANUAIS:" -ForegroundColor Yellow
    Write-Host "1. Acesse o Render Dashboard: https://dashboard.render.com" -ForegroundColor White
    Write-Host "2. Vá para o seu serviço BigWhale Backend" -ForegroundColor White
    Write-Host "3. Clique em 'Manual Deploy' > 'Deploy latest commit'" -ForegroundColor White
    Write-Host "4. Aguarde o deploy completar (2-3 minutos)" -ForegroundColor White
    Write-Host "5. Teste o endpoint: https://seu-backend.onrender.com/api/health" -ForegroundColor White
    
    Write-Host "`n🔗 LINKS IMPORTANTES:" -ForegroundColor Cyan
    Write-Host "   GitHub: https://github.com/seu-usuario/seu-repositorio" -ForegroundColor Blue
    Write-Host "   Render Dashboard: https://dashboard.render.com" -ForegroundColor Blue
    
    Write-Host "`n💡 ESPERADO APÓS DEPLOY:" -ForegroundColor Green
    Write-Host "   - Conexão SSL com PostgreSQL funcionando" -ForegroundColor White
    Write-Host "   - Health check retornando status 'healthy'" -ForegroundColor White
    Write-Host "   - Logs sem erros SSL/TLS" -ForegroundColor White
    
} else {
    Write-Host "`n❌ ERRO ao enviar para GitHub!" -ForegroundColor Red
    Write-Host "Verifique sua conexão e tente novamente." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n🎯 CORREÇÃO SSL CONCLUÍDA!" -ForegroundColor Green
Write-Host "Agora faça o redeploy manual no Render Dashboard." -ForegroundColor Yellow