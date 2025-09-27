# main.py (versão melhorada)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import threading, time, socket
from collections import defaultdict, deque
import pyshark
import os

# CONFIG — ajuste antes de rodar
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1") 
INTERFACE = os.getenv("INTERFACE", "eth0")
WINDOW_SECONDS = 5
MAX_WINDOWS = 36  # guarda últimos 3 minutos (36 * 5s)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para desenvolvimento; em produção restrinja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# estrutura: deque de janelas; cada item é {"ts": epoch_seconds, "data": defaultdict(...)}
windows = deque(maxlen=MAX_WINDOWS)
current_window = None
_lock = threading.Lock()
_first_window_ready = threading.Event()

# DNS cache simples: ip -> (hostname, expire_ts)
_dns_cache = {}
DNS_TTL = 300  # segundos

def new_window():
    # cada client -> {"in": bytes, "out": bytes, "protocols": defaultdict(int)}
    return defaultdict(lambda: {"in": 0, "out": 0, "protocols": defaultdict(int)})

def window_rotator():
    global current_window
    while True:
        with _lock:
            w = new_window()
            item = {"ts": int(time.time()), "data": w}
            windows.append(item)
            current_window = w
            # sinaliza que a primeira janela já existe
            _first_window_ready.set()
        time.sleep(WINDOW_SECONDS)

def _proto_of_packet(pkt):
    if hasattr(pkt, "tcp"):
        return "TCP"
    if hasattr(pkt, "udp"):
        return "UDP"
    if hasattr(pkt, "icmp") or hasattr(pkt, "icmpv6"):
        return "ICMP"
    return "OTHER"

def process_packet(pkt):
    """
    Atribui bytes ao cliente. IN = para SERVER_IP (dst==SERVER_IP), OUT = do SERVER_IP (src==SERVER_IP).
    Nota: pyshark pkt.length tende a ser correto; se quiser contar somente payload, ajustar.
    """
    try:
        ip = getattr(pkt, "ip", None) or getattr(pkt, "ipv6", None)
        if ip is None:
            return
        src = getattr(ip, "src", "")
        dst = getattr(ip, "dst", "")
        try:
            length = int(getattr(pkt, "length", 0))
        except Exception:
            length = 0

        proto = _proto_of_packet(pkt)

        with _lock:
            if current_window is None:
                return
            if dst == SERVER_IP and src:
                client = src
                current_window[client]["in"] += length
                # somando bytes por protocolo (mude para +1 se preferir contar pacotes)
                current_window[client]["protocols"][proto] += length
            elif src == SERVER_IP and dst:
                client = dst
                current_window[client]["out"] += length
                current_window[client]["protocols"][proto] += length
            else:
                return
    except Exception as e:
        print("Erro process_packet:", e)

def capture_loop():
    """
    Captura contínua. Espera a primeira janela estar pronta.
    Reinicia a captura em caso de erro (robustez).
    """
    # filtra por host para economizar CPU
    bpf = f'host {SERVER_IP}'
    _first_window_ready.wait()  # aguarda a primeira janela (evita race)
    while True:
        try:
            cap = pyshark.LiveCapture(interface=INTERFACE, bpf_filter=bpf)
            for pkt in cap.sniff_continuously():
                process_packet(pkt)
        except Exception as e:
            print("Capture erro:", e)
            time.sleep(2)  # aguarda antes de tentar reiniciar

def get_hostname(ip):
    # cache simples
    now = time.time()
    entry = _dns_cache.get(ip)
    if entry and entry[1] > now:
        return entry[0]
    try:
        hn = socket.gethostbyaddr(ip)[0]
    except Exception:
        hn = ip
    _dns_cache[ip] = (hn, now + DNS_TTL)
    return hn

# endpoints

@app.get("/trafego/current")
def trafego_current():
    with _lock:
        if current_window is None:
            raise HTTPException(status_code=404, detail="Nenhuma janela ainda criada")
        out = []
        for client, v in current_window.items():
            hostname = get_hostname(client)
            out.append({
                "client": client,
                "hostname": hostname,
                "in": v["in"],
                "out": v["out"],
                # protocolos já em bytes; se quiser contagem de pacotes, adapte
                "protocols": dict(v["protocols"])
            })
        out.sort(key=lambda x: x["in"] + x["out"], reverse=True)
        return {"window_seconds": WINDOW_SECONDS, "data": out}

@app.get("/trafego/history")
def trafego_history():
    """Retorna as últimas janelas com timestamps (para plot temporal)."""
    with _lock:
        resp = []
        for item in list(windows):
            snap = {"ts": item["ts"], "clients": []}
            for client, v in item["data"].items():
                snap["clients"].append({
                    "client": client,
                    "in": v["in"],
                    "out": v["out"],
                    "protocols": dict(v["protocols"])
                })
            resp.append(snap)
        return {"window_seconds": WINDOW_SECONDS, "windows": resp}

@app.get("/trafego/drilldown/{client_ip}")
def trafego_drilldown(client_ip: str):
    """Retorna a soma dos protocolos na janela atual para o client."""
    with _lock:
        if current_window is None:
            raise HTTPException(status_code=404, detail="Nenhuma janela ainda criada")
        
        # Retorna dados vazios se o cliente não existir na janela atual
        v = current_window.get(client_ip, {"in": 0, "out": 0, "protocols": {}})
        
        return {
            "client": client_ip,
            "protocols": dict(v["protocols"]),
            "in": v["in"],
            "out": v["out"]
        }

# inicialização das threads
threading.Thread(target=window_rotator, daemon=True).start()
threading.Thread(target=capture_loop, daemon=True).start()
