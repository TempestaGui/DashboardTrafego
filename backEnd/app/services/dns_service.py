# Resolve IP para hostname com cache:
# - verifica se já existe no _dns_cache e TTL ainda válido
# - senão, faz reverse DNS (gethostbyaddr)
# - salva no cache com tempo de expiração

import socket, time
import app.models.trafego as trafego
from app.config import DNS_TTL

def get_hostname(ip):
    now = time.time()
    entry = trafego._dns_cache.get(ip)
    if entry and entry[1] > now: return entry[0]
    try: hn = socket.gethostbyaddr(ip)[0]
    except: hn = ip
    trafego._dns_cache[ip] = (hn, now + DNS_TTL)
    return hn
