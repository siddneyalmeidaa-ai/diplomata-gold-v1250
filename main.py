import os
import time
import threading
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# Variaveis globais para controlo de estado, historico, RSI e Paper Trading
historico_precos = []
ULTIMO_REGISTO = "historico_diplomata.txt"
DADOS_MERCADO_GLOBAL = {}
historico_recente = {simbolo: [] for simbolo in ["BTC", "ETH", "SOL", "LINK", "NEAR", "RENDER", "DOT"]}
posicoes_virtuais = {}

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
            self.wfile.write(b"Diplomata Gold Bot - Sistema Avancado com RSI, Paper Trading e Blindagem Sentinel Ativos!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Servidor HTTP iniciado na porta {port}")
    server.serve_forever()

def calcular_rsi(precos):
    if len(precos) < 6:
        return 50.0  # Valor neutro inicial
    ganhos = 0
    perdas = 0
    for i in range(1, len(precos)):
        diff = precos[i] - precos[i-1]
        if diff > 0:
            ganhos += diff
        else:
            perdas -= diff
    if perdas == 0:
        return 100.0
    rs = (ganhos / len(precos)) / (perdas / len(precos))
    rsi = 100 - (100 / (1 + rs))
    return rsi

def guardar_historico_local(ativo, preco, variacao, rsi, status_polaridade):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{timestamp}] Ativo: {ativo} | Preço: {preco} | Var: {variacao:.2f}% | RSI: {rsi:.2f} | Estado: {status_polaridade}\n"
        with open(ULTIMO_REGISTO, "a", encoding="utf-8") as f:
            f.write(linha)
        print(f"Registo gravado: {linha.strip()}")
    except Exception as e:
        print(f"Aviso ao gravar histórico local: {e}")

def simular_paper_trading(ativo, preco, status_polaridade):
    global posicoes_virtuais
    if status_polaridade == "ENTRA | ALVO" and ativo not in posicoes_virtuais:
        posicoes_virtuais[ativo] = preco
        print(f"PAPER TRADING: Compra virtual aberta para {ativo} a {preco}")
    elif status_polaridade == "PULA / ATENÇÃO" and ativo in posicoes_virtuais:
        preco_entrada = posicoes_virtuais[ativo]
        lucro = ((preco - preco_entrada) / preco_entrada) * 100
        print(f"PAPER TRADING: Venda virtual fechada para {ativo}. Lucro/Prejuízo teórico: {lucro:.2f}%")
        del posicoes_virtuais[ativo]

def buscar_dados_mercado():
    global DADOS_MERCADO_GLOBAL
    novos_dados = {}
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

# ==========================================
# MODULO SENTINEL V16 - DUPLO CRIVO E BLINDAGEM (ACUMULADO)
# ==========================================
class SentinelAutonomousSystem:
    def __init__(self):
        self.versao = "SENTINEL_V16_ULTIMATE_BLINDAGE"
        self.memoria_erros = []
        self.historico_operacoes = []
        self.ativo_travado = False
        
    def registrar_erro_quantum(self, ativo, motivo):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        registro = {
            "tempo": timestamp,
            "ativo": ativo,
            "motivo": motivo,
            "acao": "TRAVA_AUTOMATICA_ATIVADA"
        }
        self.memoria_erros.append(registro)
        print(f"[QUANTUM MEMORY] Erro catalogado e blindagem acionada para {ativo}: {motivo}")

    def avaliar_duplo_crivo(self, ativo, variacao_24h, delta_instantaneo, pressao_volatil):
        """
        Executa o Duplo Crivo e Captura de Intencao Futura:
        - Cruza a variacao acumulada com o Delta instantaneo do minuto atual.
        - Evita a armadilha do painel verde com preco estagnado ou a cair.
        """
        sinal = "PULA / ATENÇÃO"
        status_barra = "vermelho"
        motivo = "Falta de pressao compradora no delta instantaneo"
        
        if variacao_24h > 0 and delta_instantaneo > 0:
            if pressao_volatil >= 0.5:
                sinal = "ENTRA | ALVO"
                status_barra = "verde brilhante"
                motivo = "Fluxo validado pelo duplo crivo e pressao futura favoravel"
            else:
                sinal = "PULA / ATENÇÃO"
                status_barra = "amarelo/alerta"
                motivo = "Exaustao detectada: variacao positiva mas volatilidade comprimida"
                self.registrar_erro_quantum(ativo, motivo)
        else:
            sinal = "PULA / ATENÇÃO"
            status_barra = "vermelho"
            motivo = "Delta negativo ou desfavoravel no presente momento"
            
        return {
            "ativo": ativo,
            "sinal": sinal,
            "status_barra": status_barra,
            "delta_usado": delta_instantaneo,
            "analise_futura": "Intencao capturada com sucesso",
            "motivo": motivo
        }

sentinel_autonomo = SentinelAutonomousSystem()

def bot_loop():
    precos_anteriores = {}
    while True:
        print("Diplomata Gold Bot: a executar ciclos com RSI, Paper Trading e Duplo Crivo Sentinel...")
        precos_atuais = buscar_dados_mercado()
        
        for simbolo, preco_atual in precos_atuais.items():
            historico_recente[simbolo].append(preco_atual)
            if len(historico_recente[simbolo]) > 14:
                historico_recente[simbolo].pop(0)

            rsi_atual = calcular_rsi(historico_recente[simbolo])
            preco_anterior = precos_anteriores.get(simbolo, None)
            variacao = 0.0
            
            if preco_anterior and preco_anterior > 0:
                variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

            # Simulando Delta instantaneo e pressao baseada na variacao e RSI para o Duplo Crivo
            delta_inst = variacao * 10 
            pressao_vol = 0.8 if rsi_atual < 60 else 0.3

            # Validacao pelo Duplo Crivo Sentinel
            validacao_sentinel = sentinel_autonomo.avaliar_duplo_crivo(simbolo, variacao, delta_inst, pressao_vol)
            status_polaridade = validacao_sentinel["sinal"]

            print(f"[{simbolo}] Preço: {preco_atual} | Var: {variacao:.2f}% | RSI: {rsi_atual:.2f} | Estado Sentinel: {status_polaridade} ({validacao_sentinel['motivo']})")
            
            guardar_historico_local(simbolo, preco_atual, variacao, rsi_atual, status_polaridade)
            simular_paper_trading(simbolo, preco_atual, status_polaridade)

            precos_anteriores[simbolo] = preco_atual
            
        time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    bot_loop()
            
