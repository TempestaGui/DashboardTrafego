# Configurações do sistema:
# - SERVER_IP e INTERFACE definidos por variáveis de ambiente
# - WINDOW_SECONDS: duração da janela de tráfego
# - MAX_WINDOWS: nº máximo de janelas
# - DNS_TTL: tempo de cache DNS

import os

# CONFIG — ajuste antes de rodar
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1") 
INTERFACE = os.getenv("INTERFACE", "eth0")
WINDOW_SECONDS = 5
MAX_WINDOWS = 36
DNS_TTL = 300
