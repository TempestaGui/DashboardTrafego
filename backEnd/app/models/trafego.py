# Estrutura para monitorar tráfego em janelas de tempo:
# - windows: até 36 janelas recentes
# - current_window: janela atual
# - _lock/_first_window_ready: controle de concorrência
# - _dns_cache: cache de DNS
# - new_window(): cria dicionário padrão para contar tráfego (in/out) e protocolos
from collections import defaultdict, deque
import threading

windows = deque(maxlen=36)
current_window = None
_lock = threading.Lock()
_first_window_ready = threading.Event()
_dns_cache = {}

def new_window():
    return defaultdict(lambda: {"in": 0, "out": 0, "protocols": defaultdict(int)})
