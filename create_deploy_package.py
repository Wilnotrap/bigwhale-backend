#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar pacote de deploy atualizado para Hostinger
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_deploy_package():
    """Cria um novo pacote de deploy com as correções mais recentes"""
    
    print("🚀 Criando pacote de deploy atualizado para Hostinger...")
    
    # Diretórios
    backend_dir = "./backend"
    frontend_build_dir = "./frontend/build"
    deploy_dir = "./deploy-hostinger-updated"
    
    # Limpar diretório de deploy se existir
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    
    # Criar estrutura de diretórios
    os.makedirs(deploy_dir, exist_ok=True)
    os.makedirs(f"{deploy_dir}/api", exist_ok=True)
    
    print("📁 Copiando arquivos do backend...")
    
    # Copiar arquivos do backend
    backend_files = [
        "app.py",
        "app.wsgi", 
        "requirements.txt",
        ".htaccess"
    ]
    
    for file in backend_files:
        src = os.path.join(backend_dir, file)
        if os.path.exists(src):
            shutil.copy2(src, f"{deploy_dir}/api/")
            print(f"  ✅ {file}")
    
    # Copiar diretórios do backend
    backend_dirs = [
        "auth",
        "api", 
        "models",
        "utils",
        "services",
        "database"
    ]
    
    for dir_name in backend_dirs:
        src_dir = os.path.join(backend_dir, dir_name)
        if os.path.exists(src_dir):
            dest_dir = f"{deploy_dir}/api/{dir_name}"
            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
            print(f"  ✅ {dir_name}/")
    
    # Copiar arquivo database.py se existir na raiz
    if os.path.exists("./backend/database.py"):
        shutil.copy2("./backend/database.py", f"{deploy_dir}/api/")
        print("  ✅ database.py")
    
    print("🌐 Copiando arquivos do frontend...")
    
    # Copiar build do frontend se existir
    if os.path.exists(frontend_build_dir):
        for item in os.listdir(frontend_build_dir):
            src = os.path.join(frontend_build_dir, item)
            dest = os.path.join(deploy_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)
        print("  ✅ Frontend build copiado")
    else:
        print("  ⚠️ Frontend build não encontrado")
    
    # Criar .htaccess principal
    htaccess_content = """RewriteEngine On

# Forçar HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Headers de Segurança
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# Cache para assets estáticos
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
    Header append Cache-Control "public"
</FilesMatch>

# Roteamento para React (SPA)
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api/
RewriteRule ^(.*)$ /index.html [L]

# Roteamento para API
RewriteCond %{REQUEST_URI} ^/api/
RewriteRule ^api/(.*)$ /api/app.wsgi/$1 [QSA,L]
"""
    
    with open(f"{deploy_dir}/.htaccess", 'w', encoding='utf-8') as f:
        f.write(htaccess_content)
    print("  ✅ .htaccess principal criado")
    
    # Criar .htaccess para API
    api_htaccess_content = """RewriteEngine On

# Forçar HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Roteamento para Flask via WSGI
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ app.wsgi/$1 [QSA,L]

# Headers CORS para Hostinger
Header always set Access-Control-Allow-Origin "https://bwhale.site"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With"
Header always set Access-Control-Allow-Credentials "true"

# Headers de Segurança
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
"""
    
    with open(f"{deploy_dir}/api/.htaccess", 'w', encoding='utf-8') as f:
        f.write(api_htaccess_content)
    print("  ✅ .htaccess da API criado")
    
    # Criar arquivo ZIP
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_filename = f"nautilus-deploy-{timestamp}.zip"
    
    print(f"📦 Criando arquivo ZIP: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arc_name)
    
    # Criar instruções atualizadas
    instructions = f"""🚀 INSTRUÇÕES DE DEPLOY - NAUTILUS AUTOMAÇÃO (HOSTINGER)
=======================================================

📦 Arquivo gerado: {zip_filename}
🌐 Domínio configurado: bwhale.site
🕒 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

✅ CORREÇÕES INCLUÍDAS NESTE DEPLOY:
- Correção do erro 500 no login
- Melhorias no sistema de logging
- Correção de importações duplicadas
- Configuração mais robusta do Flask-Session
- Health check aprimorado
- Tratamento de erros melhorado

📋 PRÓXIMOS PASSOS:

1. ACESSE O PAINEL HOSTINGER
   - Faça login em sua conta Hostinger
   - Acesse o hPanel (painel principal)

2. BACKUP (IMPORTANTE!)
   - Faça backup dos arquivos atuais
   - hPanel → Gerenciador de Arquivos → public_html
   - Selecione tudo → Compress → Baixe o backup

3. LIMPAR PUBLIC_HTML
   - Gerenciador de Arquivos → public_html/
   - Selecione todos os arquivos (exceto .well-known se existir)
   - Delete os arquivos antigos

4. UPLOAD DO ARQUIVO ZIP
   - No Gerenciador de Arquivos, clique em "Upload"
   - Selecione o arquivo: {zip_filename}
   - Aguarde o upload

5. EXTRAIR ARQUIVOS
   - Clique com botão direito no arquivo ZIP
   - Selecione "Extract" (Extrair)
   - Extrair para: public_html/
   - Confirme a extração

6. CONFIGURAR PERMISSÕES
   - Navegue até public_html/api/
   - Clique com botão direito na pasta "api"
   - Permissions → 755 (rwxr-xr-x)
   - Marque "Recurse into subdirectories"

7. TESTAR APLICAÇÃO
   - Frontend: https://bwhale.site
   - API: https://bwhale.site/api/health
   - Teste login com as credenciais:
     * admin@bigwhale.com / Raikamaster1@
     * willian@lexxusadm.com.br / Bigwhale202021@

🎉 SUCESSO!
Seu Nautilus Automação está rodando no Hostinger com todas as correções!

📱 URLs importantes:
- Site: https://bwhale.site
- API: https://bwhale.site/api
- Health: https://bwhale.site/api/health

---
Deploy gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Hostinger Deploy Script v2.0 - Nautilus Automação (Corrigido)
"""
    
    with open(f"INSTRUCOES_DEPLOY_{timestamp}.txt", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("\n🎉 Pacote de deploy criado com sucesso!")
    print("="*50)
    print(f"📦 Arquivo ZIP: {zip_filename}")
    print(f"📄 Instruções: INSTRUCOES_DEPLOY_{timestamp}.txt")
    print(f"🌐 Domínio: bwhale.site")
    print("\n📋 Próximos passos:")
    print(f"1. Abra o arquivo INSTRUCOES_DEPLOY_{timestamp}.txt")
    print("2. Acesse seu painel Hostinger (hPanel)")
    print("3. Siga as instruções passo a passo")
    print("4. Teste sua aplicação após o deploy")
    
    # Limpar diretório temporário
    shutil.rmtree(deploy_dir)
    
    return zip_filename

if __name__ == "__main__":
    create_deploy_package()