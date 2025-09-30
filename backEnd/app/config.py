import os

# CONFIG — ajuste antes de rodar
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1") 
INTERFACE = os.getenv("INTERFACE", "eth0")
WINDOW_SECONDS = 5
MAX_WINDOWS = 36
DNS_TTL = 300
