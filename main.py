import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# Variáveis globais para controlo de estado e histórico local
historico_precos = []
ULTIMO_REGISTO = "historico_diplomata.txt"

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Diplomata Gold Bot - Sistema Completo com Historico, Alertas e Regras de Polaridade Ativo!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Servidor HTTP iniciado na porta {port}")
    server.serve_forever()

def guardar_historico_local(preco, variacao, status_polaridade):
    # Registo contínuo em ficheiro local para auditoria e análises posteriores
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{timestamp}] Preço: {preco} | Variação: {variacao:.2f}% | Estado: {status_polaridade}\n"
        with open(ULTIMO_REGISTO, "a", encoding="utf-8") as f:
            f.write(linha)
        print(f"Registo gravado no histórico local: {linha.strip()}")
    except Exception as e:
        print(f"Aviso ao gravar histórico local: {e}")

def disparar_alerta(mensagem):
    # Estrutura de alertas para notificação de limiares e eventos críticos
    print(f"ALERTA DIPLOMATA GOLD -> {mensagem}")

def buscar_dados_mercado():
    try:
        url = "https://api.coincap.io/v2/assets/bitcoin"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            preco = float(dados['data']['priceUsd'])
            return preco
    except Exception as e:
        print(f"Aviso na recolha de dados: {e}")
    return None

def bot_loop():
    preco_anterior = None
    while True:
        print("Diplomata Gold Bot: a executar ciclos de analise e regras de polaridade...")
        preco_atual = buscar_dados_mercado()
        
        if preco_atual:
            variacao = 0.0
            if preco_anterior and preco_anterior > 0:
                variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

            # Regras de polaridade e tomada de decisão combinadas
            if variacao > 0.05:
                status_polaridade = "ALTA / POSITIVA"
            elif variacao < -0.05:
                status_polaridade = "QUEDA / NEGATIVA"
            else:
                status_polaridade = "LATERAL / NEUTRO"

            print(f"Preço atual: {preco_atual} | Variação calculada: {variacao:.2f}% | Polaridade: {status_polaridade}")
            
            # Grava no histórico local
            guardar_historico_local(preco_atual, variacao, status_polaridade)

            # Aciona alertas com base em limiares operacionais
            if abs(variacao) > 0.10:
                disparar_alerta(f"Variação expressiva detetada: {variacao:.2f}%! Monitorizar ativo.")

            preco_anterior = preco_atual
            
        time.sleep(60)

if __name__ == "__main__":
    # Inicia o servidor web em segundo plano para o Render aceitar o deploy
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Roda o loop principal do robô com todas as regras integradas
    bot_loop()
    
