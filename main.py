import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Diplomata Gold Bot ativo e operando!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Servidor HTTP iniciado na porta {port}")
    server.serve_forever()

def bot_loop():
    while True:
        print("Diplomata Gold Bot: executando varredura...")
        # Adiciona aqui a tua lógica e chamadas com requests se necessário
        time.sleep(60)

if __name__ == "__main__":
    # Inicia o servidor web em segundo plano para o Render aceitar o deploy
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Roda o loop principal do robô
    bot_loop()
  
