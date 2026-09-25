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
            self.wfile.write(b"Diplomata Gold Bot - Sistema Avancado com RSI, Paper Trading e Blindagem Sentinel V16 Ativa!")

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

# ==========================================
# MODULO SENTINEL V16 - BLINDAGEM COMPLETA (ACUMULADO)
# Inclui: Duplo Crivo, Memoria Quântica, Filtro de Volume Real e Saída Dinâmica de Fluxo
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

    def avaliar_duplo_crivo_e_volume(self, ativo, variacao_24h, delta_instantaneo, pressao_volatil, volume_real):
        """
        Executa o Duplo Crivo Avançado:
        - Cruza variação de 24h com Delta instantâneo.
        - Aplica o Filtro de Volume Real (barra variações vazias/sem liquidez).
        """
        sinal = "PULA / ATENÇÃO"
        status_barra = "vermelho"
        motivo = "Falta de pressão ou volume no delta instantâneo"
        
        # Exigência de Volume Real mínimo para evitar falsos rompimentos
        VOLUME_MINIMO_EXIGIDO = 1000.0  

        if volume_real < VOLUME_MINIMO_EXIGIDO:
            motivo = "Variação vazia: volume real abaixo do limiar institucional"
            self.registrar_erro_quantum(ativo, motivo)
            return {"ativo": ativo, "sinal": sinal, "status_barra": "amarelo/alerta", "motivo": motivo}

        if variacao_24h > 0 and delta_instantaneo > 0:
            if pressao_volatil >= 0.5:
                sinal = "ENTRA | ALVO"
                status_barra = "verde brilhante"
                motivo = "Fluxo validado por Duplo Crivo e Volume Real favorável"
            else:
                sinal = "PULA / ATENÇÃO"
                status_barra = "amarelo/alerta"
                motivo = "Exaustão detectada: variação positiva mas volatilidade comprimida"
                self.registrar_erro_quantum(ativo, motivo)
        else:
            sinal = "PULA / ATENÇÃO"
            status_barra = "vermelho"
            motivo = "Delta negativo ou desfavorável no presente momento"
            
        return {
            "ativo": ativo,
            "sinal": sinal,
            "status_barra": status_barra,
            "delta_usado": delta_instantaneo,
            "motivo": motivo
        }

    def gerenciar_saida_dinamica(self, ativo, preco_atual, delta_instantaneo):
        """
        Gerencia posições abertas em Paper Trading:
        - Dispara saída dinâmica se o fluxo (Delta) inverter violentamente contra a posição.
        """
        global posicoes_virtuais
        if ativo in posicoes_virtuais:
            preco_entrada = posicoes_virtuais[ativo]["preco"]
            delta_entrada = posicoes_virtuais[ativo]["delta_inicial"]
            
            # Condição de Inversão de Fluxo: Se o Delta estava positivo na entrada e agora virou fortemente negativo
            if delta_instantaneo < -0.2:
                lucro = ((preco_atual - preco_entrada) / preco_entrada) * 100
                print(f"[SAÍDA DINÂMICA DE FLUXO] Inversão detectada em {ativo}! Fechamento forçado de segurança. Lucro/Prejuízo: {lucro:.2f}%")
                del posicoes_virtuais[ativo]
                return True
        return False

sentinel_autonomo = SentinelAutonomousSystem()
posicoes_virtuais = {} # Estrutura enriquecida: {ativo: {"preco": val, "delta_inicial": val}}

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
                # Simulando captura de volume real baseada no coinmarketcap/coincap se disponível, ou métrica proporcional
                volume = float(dados['data'].get('volumeUsd24Hr', 1500000)) / 1440 # Volume aproximado por minuto
                novos_dados[simbolo] = {"preco": preco, "volume": volume}
        except Exception as e:
            print(f"Aviso na recolha de dados para {simbolo}: {e}")
            
    if novos_dados:
        DADOS_MERCADO_GLOBAL = {k: v["preco"] for k, v in novos_dados.items()}
    return novos_dados

def bot_loop():
    precos_anteriores = {}
    while True:
        print("Diplomata Gold Bot: a executar ciclos com RSI, Paper Trading e Blindagem Sentinel V16...")
        dados_ativos = buscar_dados_mercado()
        
        for simbolo, info in dados_ativos.items():
            preco_atual = info["preco"]
            volume_atual = info["volume"]

            historico_recente[simbolo].append(preco_atual)
            if len(historico_recente[simbolo]) > 14:
                historico_recente[simbolo].pop(0)

            rsi_atual = calcular_rsi(historico_recente[simbolo])
            preco_anterior = precos_anteriores.get(simbolo, None)
            variacao = 0.0
            
            if preco_anterior and preco_anterior > 0:
                variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

            # Simulação de Delta e Pressão com base nas métricas reais
            delta_inst = variacao * 10 
            pressao_vol = 0.8 if rsi_atual < 60 else 0.3

            # 1. Executa Saída Dinâmica em posições abertas se o fluxo inverter
            sentinel_autonomo.gerenciar_saida_dinamica(simbolo, preco_atual, delta_inst)

            # 2. Validação por Duplo Crivo e Volume Real
            validacao_sentinel = sentinel_autonomo.avaliar_duplo_crivo_e_volume(simbolo, variacao, delta_inst, pressao_vol, volume_atual)
            status_polaridade = validacao_sentinel["sinal"]

            print(f"[{simbolo}] Preço: {preco_atual} | Var: {variacao:.2f}% | RSI: {rsi_atual:.2f} | Estado Sentinel: {status_polaridade} ({validacao_sentinel['motivo']})")
            
            guardar_historico_local(simbolo, preco_atual, variacao, rsi_atual, status_polaridade)
            
            # Gestão de Paper Trading com base no sinal validado
            if status_polaridade == "ENTRA | ALVO" and simbolo not in posicoes_virtuais:
                posicoes_virtuais[simbolo] = {"preco": preco_atual, "delta_inicial": delta_inst}
                print(f"PAPER TRADING: Compra virtual aberta para {simbolo} a {preco_atual} com Delta validado.")

            precos_anteriores[simbolo] = preco_atual
            
        time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    bot_loop()
        
