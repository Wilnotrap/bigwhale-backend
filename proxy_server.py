#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
import threading
import time
from urllib.parse import urlparse, parse_qs

class NautilusProxyHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, auth-userid')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests - proxy para Nautilus"""
        if self.path == '/api/nautilus/login':
            self.handle_nautilus_login()
        else:
            super().do_POST()
    
    def do_GET(self):
        """Handle GET requests - proxy para Nautilus ou serve arquivos"""
        if self.path == '/api/nautilus/active-operations':
            self.handle_nautilus_operations()
        else:
            super().do_GET()
    
    def handle_nautilus_login(self):
        """Proxy para login do Nautilus"""
        try:
            # Ler dados do request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print("🔐 Fazendo login no Nautilus...")
            
            # Criar requisição para o Nautilus
            nautilus_url = "https://bw.mdsa.com.br/login"
            req = urllib.request.Request(
                nautilus_url,
                data=post_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Origin': 'https://bw-admin.mdsa.com.br',
                    'Referer': 'https://bw-admin.mdsa.com.br/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # Fazer requisição
            with urllib.request.urlopen(req, timeout=30) as response:
                result = response.read().decode('utf-8')
                
                print("✅ Login realizado com sucesso!")
                
                # Enviar resposta para o cliente
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(result.encode('utf-8'))
                
        except urllib.error.HTTPError as e:
            print(f"❌ Erro HTTP no login: {e.code}")
            self.send_error_response(e.code, f"Erro no login: {e.reason}")
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            self.send_error_response(500, f"Erro interno: {str(e)}")
    
    def handle_nautilus_operations(self):
        """Proxy para operações ativas do Nautilus"""
        try:
            # Extrair headers de autorização
            auth_token = self.headers.get('Authorization', '')
            user_id = self.headers.get('auth-userid', '')
            
            print("📊 Buscando operações ativas...")
            
            # Criar requisição para o Nautilus
            nautilus_url = "https://bw.mdsa.com.br/operation/active-operations"
            req = urllib.request.Request(
                nautilus_url,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': auth_token,
                    'auth-userid': user_id,
                    'Origin': 'https://bw-admin.mdsa.com.br',
                    'Referer': 'https://bw-admin.mdsa.com.br/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # Fazer requisição
            with urllib.request.urlopen(req, timeout=30) as response:
                result = response.read().decode('utf-8')
                
                print("✅ Operações obtidas com sucesso!")
                
                # Enviar resposta para o cliente
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(result.encode('utf-8'))
                
        except urllib.error.HTTPError as e:
            print(f"❌ Erro HTTP nas operações: {e.code}")
            self.send_error_response(e.code, f"Erro nas operações: {e.reason}")
        except Exception as e:
            print(f"❌ Erro nas operações: {e}")
            self.send_error_response(500, f"Erro interno: {str(e)}")
    
    def send_error_response(self, code, message):
        """Enviar resposta de erro com CORS"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = json.dumps({"error": message})
        self.wfile.write(error_response.encode('utf-8'))
    
    def end_headers(self):
        # Adicionar headers CORS para todos os responses
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, auth-userid')
        super().end_headers()

def start_proxy_server():
    """Inicia servidor proxy na porta 8080"""
    PORT = 8080
    
    try:
        print("🌐 Iniciando servidor proxy Nautilus...")
        print(f"📂 Diretório: {os.getcwd()}")
        print(f"🔗 URL: http://localhost:{PORT}")
        print("-" * 50)
        
        with socketserver.TCPServer(("", PORT), NautilusProxyHandler) as httpd:
            print(f"✅ Servidor proxy rodando em http://localhost:{PORT}")
            print(f"📄 Acesse: http://localhost:{PORT}/test_active_operations_proxy.html")
            print("\n🚀 Abrindo navegador automaticamente...")
            print("⏹️  Para parar o servidor: Ctrl+C")
            print("-" * 50)
            
            # Abrir navegador automaticamente após 2 segundos
            def open_browser():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{PORT}/test_active_operations_proxy.html')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Iniciar servidor
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Porta {PORT} já está em uso!")
            print("💡 Pressione Ctrl+C no terminal anterior para parar o servidor")
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor interrompido pelo usuário")
        print("✅ Servidor encerrado com sucesso!")

if __name__ == "__main__":
    import os
    start_proxy_server() 