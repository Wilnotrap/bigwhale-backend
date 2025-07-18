#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import threading
import time

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Adicionar headers para permitir CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, auth-userid')
        super().end_headers()

def start_server():
    """Inicia servidor local na porta 8080"""
    PORT = 8080
    
    try:
        print("🌐 Iniciando servidor local...")
        print(f"📂 Diretório: {os.getcwd()}")
        print(f"🔗 URL: http://localhost:{PORT}")
        print("-" * 50)
        
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"✅ Servidor rodando em http://localhost:{PORT}")
            print(f"📄 Acesse: http://localhost:{PORT}/test_active_operations.html")
            print("\n🚀 Abrindo navegador automaticamente...")
            print("⏹️  Para parar o servidor: Ctrl+C")
            print("-" * 50)
            
            # Abrir navegador automaticamente após 2 segundos
            def open_browser():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{PORT}/test_active_operations.html')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Iniciar servidor
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Porta {PORT} já está em uso!")
            print("💡 Tente fechar outros servidores ou usar outra porta")
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor interrompido pelo usuário")
        print("✅ Servidor encerrado com sucesso!")

if __name__ == "__main__":
    start_server() 