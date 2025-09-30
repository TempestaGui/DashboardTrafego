from collections import defaultdict, deque
import threading

windows = deque(maxlen=36)
current_window = None
_lock = threading.Lock()
_first_window_ready = threading.Event()
_dns_cache = {}

def new_window():
    return defaultdict(lambda: {"in": 0, "out": 0, "protocols": defaultdict(int)})
