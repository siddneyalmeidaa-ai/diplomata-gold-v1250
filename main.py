import os
import time
import threading
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# MODULO DE MEMÓRIA QUÂNTICA PERSISTENTE (ACUMULADO)
# ==========================================
FICHEIRO_MEMORIA_QUANTICA = "memoria_sentinel.json"

class MotorDeMemoriaAdaptativaPersistente:
    def __init__(self, nome_ficheiro=FICHEIRO_MEMORIA_QUANTICA):
        self.nome_ficheiro = nome_ficheiro
        self.historico_eventos = []
        self.padroes_bloqueados = {}
        self.carregar_memoria()

    def carregar_memoria(self):
        if os.path.exists(self.nome_ficheiro):
            try:
                with open(self.nome_ficheiro, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.historico_eventos = dados.get("eventos", [])
                    self.padroes_bloqueados = dados.get("bloqueios", {})
                print(f"[QUANTUM MEMORY] Histórico carregado com sucesso de '{self.nome_ficheiro}'.")
            except Exception as e:
                print(f"[AVISO] Erro ao carregar ficheiro de memória: {e}")

    def guardar_memoria(self):
        try:
            dados = {
                "eventos": self.historico_eventos,
                "bloqueios": self.padroes_bloqueados
            }
            with open(self.nome_ficheiro, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[AVISO] Erro ao gravar ficheiro de memória: {e}")

    def registar_experiencia(self, ativo, contexto, resultado):
        registo = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ativo": ativo,
            "contexto": contexto,
            "resultado": resultado
        }
        self.historico_eventos.append(registo)
        
        if resultado == "ARMADILHA":
            self.padroes_bloqueados[ativo] = time.time()
            
        self.guardar_memoria()

    def consultar_passado(self, ativo):
        if ativo in self.padroes_bloqueados:
            tempo_decorrido = time.time() - self.padroes_bloqueados[ativo]
            if tempo_decorrido < 300: # 5 minutos de quarentena
                return "BLOQUEADO_POR_HISTORICO_RECENTE"

        falhas_anteriores = sum(
            1 for e in self.historico_eventos 
            if e["ativo"] == ativo and e["resultado"] == "ARMADILHA"
        )
        
        if falhas_anteriores >= 3:
            return "ALTA_PROBABILIDADE_DE_ERRO"
            
        return "APROVADO"

motor_memoria = MotorDeMemoriaAdaptativaPersistente()

# ==========================================
# GESTOR DE HISTERESE (CONFIRMAÇÃO TEMPORAL)
# ==========================================
class GestorHisterese:
    def __init__(self, ciclos_necessarios=3):
        self.ciclos_necessarios = ciclos_necessarios
        self.candidato_estado = {}
        self.contador_ciclos = {}
        self.estado_estavel = {}

    def avaliar(self, ativo, novo_estado_proposto):
        estado_atual = self.estado_estavel.get(ativo, "LATERAL")
        candidato_atual = self.candidato_estado.get(ativo, None)

        if novo_estado_proposto == candidato_atual:
            self.contador_ciclos[ativo] = self.contador_ciclos.get(ativo, 0) + 1
        else:
            self.candidato_estado[ativo] = novo_estado_proposto
            self.contador_ciclos[ativo] = 1

        # Se atingiu o limiar de persistência, consolida o estado (Elimina o flickering)
        if self.contador_ciclos[ativo] >= self.ciclos_necessarios:
            self.estado_estavel[ativo] = self.candidato_estado[ativo]

        return self.estado_estavel.get(ativo, "LATERAL")

gestor_histerese = GestorHisterese(ciclos_necessarios=3)

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
        elif self.path == "/api/diagnostico":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            dados_memoria = {}
            if os.path.exists(FICHEIRO_MEMORIA_QUANTICA):
                with open(FICHEIRO_MEMORIA_QUANTICA, "r", encoding="utf-8") as f:
                    dados_memoria = json.load(f)
            self.wfile.write(json.dumps(dados_memoria, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Diplomata Gold Bot - Sistema Avancado com RSI, Paper Trading, Memoria Quantica e Histerese!")

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
    return novos_dados

def bot_loop():
    precos_anteriores = {}
    while True:
        print("Diplomata Gold Bot: a executar ciclos com RSI, Paper Trading, Memória Quântica e Histerese...")
        precos_atuais = buscar_dados_mercado()
        
        novos_dados_api = {}
        
        for simbolo, preco_atual in precos_atuais.items():
            historico_recente[simbolo].append(preco_atual)
            if len(historico_recente[simbolo]) > 14:
                historico_recente[simbolo].pop(0)

            rsi_atual = calcular_rsi(historico_recente[simbolo])
            preco_anterior = precos_anteriores.get(simbolo, None)
            variacao = 0.0
            
            if preco_anterior and preco_anterior > 0:
                variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

            # Consulta ao Passado via Memória Quântica
            status_memoria = motor_memoria.consultar_passado(simbolo)
            
            if status_memoria != "APROVADO":
                bruto_polaridade = "PULA / ATENÇÃO"
                print(f"[{simbolo}] BLOQUEADO pela Memória Quântica ({status_memoria})")
                motor_memoria.registar_experiencia(simbolo, {"variacao": variacao, "rsi": rsi_atual}, "ARMADILHA")
            else:
                if variacao > 0.03 or rsi_atual < 35:
                    bruto_polaridade = "ENTRA | ALVO"
                    motor_memoria.registar_experiencia(simbolo, {"variacao": variacao, "rsi": rsi_atual}, "SUCESSO")
                elif variacao < -0.03 or rsi_atual > 65:
                    bruto_polaridade = "PULA / ATENÇÃO"
                    motor_memoria.registar_experiencia(simbolo, {"variacao": variacao, "rsi": rsi_atual}, "ARMADILHA")
                else:
                    bruto_polaridade = "LATERAL"

            # Aplicação da Histerese (Exige 3 ciclos consistentes para consolidar o estado)
            status_polaridade = gestor_histerese.avaliar(simbolo, bruto_polaridade)

            print(f"[{simbolo}] Preço: {preco_atual} | Var: {variacao:.2f}% | RSI: {rsi_atual:.2f} | Estado Estável (Histerese): {status_polaridade}")
            
            guardar_historico_local(simbolo, preco_atual, variacao, rsi_atual, status_polaridade)
            simular_paper_trading(simbolo, preco_atual, status_polaridade)

            # Empacota os dados validados para a API consumir limpo
            novos_dados_api[simbolo] = {
                "preco": preco_atual,
                "variacao": variacao,
                "rsi": rsi_atual,
                "estado": status_polaridade
            }

            precos_anteriores[simbolo] = preco_atual
            
        global DADOS_MERCADO_GLOBAL
        DADOS_MERCADO_GLOBAL = novos_dados_api
            
        time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    bot_loop()
        
