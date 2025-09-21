import random
from collections import defaultdict
import threading
import time


# Cria um dicionário especial que já vem com valores padrão.
# Cada nova chave (um IP) terá como valor inicial um dicionário com:
# - tráfego "in" (entrada)
# - tráfego "out" (saída)
# - protocolos usados (inicialmente vazio)
traffic_data = defaultdict(lambda: {"in": 0, "out": 0, "protocols": {}})

def start_capture():
    # Função interna que simula a captura de tráfego de rede
    def simulate_traffic():
        while True:
            # Define um IP fixo (neste caso sempre 192.168.1.10)
            ip = "192.168.1.10"

            # Atualiza os bytes de entrada e saída de forma aleatória
            traffic_data[ip]["in"] += random.randint(100, 1000)
            traffic_data[ip]["out"] += random.randint(100, 1000)

            # Simula estatísticas de protocolos
            traffic_data[ip]["protocols"]["TCP"] = random.randint(500, 2000)
            traffic_data[ip]["protocols"]["UDP"] = random.randint(200, 1000)

            # Aguarda 5 segundos antes de gerar novos dados
            time.sleep(5)

            # Inicia a função simulate_traffic em uma thread separada (em paralelo)
            # Isso permite que o programa principal continue rodando sem ficar travado no loop infinito.
    threading.Thread(target=simulate_traffic, daemon=True).start()
