# 🖼️ Script de Otimização de Assets
# Nautilus Automação - Asset Optimization

Write-Host "🖼️ Otimizando assets para produção..." -ForegroundColor Blue

# Verificar se ImageMagick está instalado
if (-not (Get-Command "magick" -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  ImageMagick não encontrado. Instalando via Chocolatey..." -ForegroundColor Yellow
    
    if (Get-Command "choco" -ErrorAction SilentlyContinue) {
        choco install imagemagick -y
    } else {
        Write-Host "❌ Chocolatey não encontrado. Instale ImageMagick manualmente." -ForegroundColor Red
        Write-Host "   Download: https://imagemagick.org/script/download.php#windows" -ForegroundColor Cyan
        return
    }
}

# Otimizar imagens
$assetsDir = "./frontend/src/assets"
if (Test-Path $assetsDir) {
    Get-ChildItem -Path $assetsDir -Recurse -Include *.jpg,*.jpeg,*.png | ForEach-Object {
        $originalSize = $_.Length
        
        Write-Host "🔧 Otimizando: $($_.Name)" -ForegroundColor Blue
        
        # Otimizar imagem
        $outputPath = $_.FullName
        magick "$($_.FullName)" -strip -quality 85 -resize "1920x1920>" "$outputPath"
        
        $newSize = (Get-Item $outputPath).Length
        $savings = [math]::Round((($originalSize - $newSize) / $originalSize) * 100, 1)
        
        Write-Host "   ✅ Reduzido em $savings% ($([math]::Round($originalSize/1KB, 1))KB → $([math]::Round($newSize/1KB, 1))KB)" -ForegroundColor Green
    }
    
    Write-Host "✅ Otimização de imagens concluída" -ForegroundColor Green
} else {
    Write-Host "⚠️  Diretório de assets não encontrado" -ForegroundColor Yellow
}
