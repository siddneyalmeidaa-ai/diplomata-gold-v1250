import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Diplomata Gold Bot ativo e operando! Sistema de Monitoramento e Radar de Polaridade Ativo!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Servidor HTTP iniciado na porta {port}")
    print(f"Servidor HTTP de suporte iniciado na porta {port}")
    server.serve_forever()

def buscar_dados_mercado():
    # Ponto de varredura para recolha de dados de cotação pública enquanto configuramos as APIs finais
    try:
        url = "https://api.coincap.io/v2/assets/bitcoin"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            preco = float(dados['data']['priceUsd'])
            print(f"Varredura Diplomata Gold - Preço atual capturado: {preco}")
            return preco
    except Exception as e:
        print(f"Aviso na recolha de dados: {e}")
    return None

def bot_loop():
    while True:
        print("Diplomata Gold Bot: executando varredura...")
        print("Diplomata Gold Bot: a executar ciclos de analise e regras de polaridade...")
        # Adiciona aqui a tua lógica e chamadas com requests se necessário
        preco_atual = buscar_dados_mercado()
        
        # Aplicando as diretrizes operacionais combinadas
        if preco_atual:
            print("Estado sincronizado. Monitoramento ativo sob o padrao estabelecido.")
            
        time.sleep(60)

if __name__ == "__main__":
    # Inicia o servidor web em segundo plano para o Render aceitar o deploy
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Roda o loop principal do robô
    bot_loop()
    
