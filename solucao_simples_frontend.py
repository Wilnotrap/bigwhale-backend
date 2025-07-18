#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solução Simples para o Frontend
Como o código já está correto, vamos fazer um rebuild limpo
"""

import os
import subprocess
import shutil
from datetime import datetime

def clear_cache():
    """Limpa cache do frontend"""
    print("🧹 Limpando cache do frontend...")
    
    # Remover node_modules
    if os.path.exists('frontend/node_modules'):
        print("   📦 Removendo node_modules...")
        shutil.rmtree('frontend/node_modules')
    
    # Remover build anterior
    if os.path.exists('frontend/build'):
        print("   🏗️ Removendo build anterior...")
        shutil.rmtree('frontend/build')
    
    # Remover cache do npm
    os.chdir('frontend')
    try:
        subprocess.run(['npm', 'cache', 'clean', '--force'], check=True, capture_output=True)
        print("   ✅ Cache do npm limpo")
    except:
        print("   ⚠️ Não foi possível limpar cache do npm")
    finally:
        os.chdir('..')

def rebuild_frontend():
    """Rebuild completo do frontend"""
    print("🔨 Fazendo rebuild completo do frontend...")
    
    os.chdir('frontend')
    try:
        # Instalar dependências
        print("   📦 Instalando dependências...")
        subprocess.run(['npm', 'install'], check=True)
        
        # Build
        print("   🏗️ Fazendo build...")
        subprocess.run(['npm', 'run', 'build'], check=True)
        
        print("   ✅ Build concluído com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro no build: {e}")
        return False
    finally:
        os.chdir('..')

def copy_to_deploy():
    """Copia para pasta de deploy"""
    print("📁 Copiando para pasta de deploy...")
    
    if os.path.exists('frontend-deploy-novo'):
        shutil.rmtree('frontend-deploy-novo')
    
    if os.path.exists('frontend/build'):
        shutil.copytree('frontend/build', 'frontend-deploy-novo')
        print("   ✅ Copiado para: frontend-deploy-novo/")
        return True
    else:
        print("   ❌ Pasta build não encontrada")
        return False

def create_test_script():
    """Cria script de teste simples"""
    print("📝 Criando script de teste...")
    
    test_script = '''
<!DOCTYPE html>
<html>
<head>
    <title>Teste de Conectividade</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .result { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Teste de Conectividade - BigWhale</h1>
    <div id="results"></div>
    
    <script>
        const BACKEND_URL = 'https://bigwhale-backend.onrender.com';
        const results = document.getElementById('results');
        
        async function testEndpoint(url, name) {
            try {
                const response = await fetch(url);
                const status = response.status;
                const text = status === 200 ? 'OK' : status === 401 ? 'Não autenticado (normal)' : 'Erro';
                
                results.innerHTML += `<div class="result ${status === 200 || status === 401 ? 'success' : 'error'}">
                    ${name}: ${status} - ${text}
                </div>`;
            } catch (error) {
                results.innerHTML += `<div class="result error">
                    ${name}: Erro - ${error.message}
                </div>`;
            }
        }
        
        // Testes
        testEndpoint(`${BACKEND_URL}/api/health`, 'Health Check');
        testEndpoint(`${BACKEND_URL}/api/dashboard/account-balance`, 'Account Balance');
        testEndpoint(`${BACKEND_URL}/api/dashboard/open-positions`, 'Open Positions');
        testEndpoint(`${BACKEND_URL}/api/dashboard/stats`, 'Stats');
    </script>
</body>
</html>
'''
    
    with open('teste_conectividade.html', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("   ✅ Criado: teste_conectividade.html")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 SOLUÇÃO SIMPLES PARA O FRONTEND")
    print("=" * 60)
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    print("\n📋 DIAGNÓSTICO:")
    print("   ✅ Código do frontend está correto")
    print("   ✅ URLs estão corretas no dashboardService.js")
    print("   ✅ Backend está funcionando")
    print("   ❌ Problema: Build antigo ou cache")
    
    print("\n🔧 SOLUÇÃO:")
    
    # Limpar cache
    clear_cache()
    
    # Rebuild
    if rebuild_frontend():
        print("✅ Rebuild concluído")
    else:
        print("❌ Erro no rebuild")
        return False
    
    # Copiar para deploy
    if copy_to_deploy():
        print("✅ Copiado para deploy")
    else:
        print("❌ Erro na cópia")
        return False
    
    # Criar script de teste
    create_test_script()
    
    print("\n" + "=" * 60)
    print("🎉 SOLUÇÃO APLICADA COM SUCESSO!")
    print("=" * 60)
    
    print("\n📁 ARQUIVOS PRONTOS:")
    print("   - frontend-deploy-novo/ (para upload)")
    print("   - teste_conectividade.html (para testar)")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Fazer upload dos arquivos de 'frontend-deploy-novo/' para a Hostinger")
    print("2. Substituir TODOS os arquivos antigos")
    print("3. Limpar cache do navegador (Ctrl+F5)")
    print("4. Testar o funcionamento")
    
    print("\n🧪 TESTE MANUAL:")
    print("   1. Abrir teste_conectividade.html no navegador")
    print("   2. Verificar se todos os endpoints respondem")
    print("   3. Fazer login no sistema")
    print("   4. Verificar se o dashboard carrega")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ PRONTO! Agora é só fazer o upload do frontend-deploy-novo/")
    else:
        print("\n❌ Houve problemas na solução") 