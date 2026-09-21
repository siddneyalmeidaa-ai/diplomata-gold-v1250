import os
import time
import threading
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# Variáveis globais para controlo de estado, histórico e dados para a interface
historico_precos = []
ULTIMO_REGISTO = "historico_diplomata.txt"
DADOS_MERCADO_GLOBAL = {}

# Lista de ativos alinhada com o painel visual (IDs da API Coincap)
ATIVOS_MONITORIZADOS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "LINK": "chainlink",
    "NEAR": "near",
    "RENDER": "render-token",
    "DOT": "polkadot"
}

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Sugestão 1: Endpoint de API para ligar o bot diretamente à interface visual
        if self.path == "/api/dados":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(DADOS_MERCADO_GLOBAL, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Diplomata Gold Bot - Sistema Multi-Ativo, Historico e API Ativos!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Servidor HTTP iniciado na porta {port}")
    server.serve_forever()

def guardar_historico_local(ativo, preco, variacao, status_polaridade):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{timestamp}] Ativo: {ativo} | Preço: {preco} | Variação: {variacao:.2f}% | Estado: {status_polaridade}\n"
        with open(ULTIMO_REGISTO, "a", encoding="utf-8") as f:
            f.write(linha)
        print(f"Registo gravado: {linha.strip()}")
    except Exception as e:
        print(f"Aviso ao gravar histórico local: {e}")

def disparar_alerta(mensagem):
    print(f"ALERTA DIPLOMATA GOLD -> {mensagem}")

def buscar_dados_mercado():
    global DADOS_MERCADO_GLOBAL
    novos_dados = {}
    
    # Sugestão 3: Expandir para múltiplos ativos em simultâneo
    for simbolo, coin_id in ATIVOS_MONITORIZADOS.items():
        try:
            url = f"https://api.coincap.io/v2/assets/{coin_id}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                dados = response.json()
                preco = float(dados['data']['priceUsd'])
                novos_dados[simbolo] = preco
        except Exception as e:
            print(f"Aviso na recolha de dados para {simbolo}: {e}")
            
    if novos_dados:
        DADOS_MERCADO_GLOBAL = novos_dados
    return novos_dados

def bot_loop():
    precos_anteriores = {}
    while True:
        print("Diplomata Gold Bot: a executar ciclos de análise multi-ativo...")
        precos_atuais = buscar_dados_mercado()
        
        for simbolo, preco_atual in precos_atuais.items():
            preco_anterior = precos_anteriores.get(simbolo, None)
            variacao = 0.0
            
            if preco_anterior and preco_anterior > 0:
                variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

            # Sugestão 2: Regras dinâmicas e estados visuais (ENTRA | ALVO / LATERAL)
            if variacao > 0.03:
                status_polaridade = "ENTRA | ALVO"
            elif variacao < -0.03:
                status_polaridade = "PULA / ATENÇÃO"
            else:
                status_polaridade = "LATERAL"

            print(f"[{simbolo}] Preço: {preco_atual} | Variação: {variacao:.2f}% | Estado: {status_polaridade}")
            
            # Grava no histórico local
            guardar_historico_local(simbolo, preco_atual, variacao, status_polaridade)

            # Aciona alertas se houver variação expressiva
            if abs(variacao) > 0.10:
                disparar_alerta(f"Variação expressiva no ativo {simbolo}: {variacao:.2f}%!")

            precos_anteriores[simbolo] = preco_atual
            
        time.sleep(60)

if __name__ == "__main__":
    # Inicia o servidor web em segundo plano com suporte a API
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Roda o motor principal multi-ativo
    bot_loop()
            
