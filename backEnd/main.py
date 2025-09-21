# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import threading, time
from collections import defaultdict, deque
import pyshark
import os
import socket

# CONFIG — ajuste antes de rodar
SERVER_IP = "192.168.0.132"       # seu IP real
INTERFACE = "wlxd03745886595" 
WINDOW_SECONDS = 5
MAX_WINDOWS = 36  # guarda últimos 3 minutos (36 * 5s) — ajuste se quiser

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# estrutura: deque de janelas, cada janela é dict {client_ip: {"in":bytes, "out":bytes, "protocols":{...}}}
windows = deque(maxlen=MAX_WINDOWS)
current_window = None
_lock = threading.Lock()

def new_window():
    return defaultdict(lambda: {"in": 0, "out": 0, "protocols": defaultdict(int)})

def window_rotator():
    global current_window
    while True:
        with _lock:
            current_window = new_window()
            windows.append(current_window)
        time.sleep(WINDOW_SECONDS)
        

def process_packet(pkt):
    """
    Determina se o pacote envolve SERVER_IP; se sim, atribui bytes ao client (src/dst) e
    marca in/out (in = para SERVER_IP, out = do SERVER_IP).
    """
    try:
        ip = getattr(pkt, "ip", None)
        if ip is None:
            return
        src = getattr(ip, "src", "")
        dst = getattr(ip, "dst", "")
        length = int(getattr(pkt, "length", 0))
        # descobrir protocolo básico
        proto = "OTHER"
        if hasattr(pkt, "tcp"):
            proto = "TCP"
        elif hasattr(pkt, "udp"):
            proto = "UDP"
        elif hasattr(pkt, "icmp"):
            proto = "ICMP"

        with _lock:
            if current_window is None:
                return
            # pacote vindo de client para server => server is dst => IN
            if dst == SERVER_IP and src:
                client = src
                current_window[client]["in"] += length
                current_window[client]["protocols"][proto] += 1
            # pacote vindo do server para client => server is src => OUT
            elif src == SERVER_IP and dst:
                client = dst
                current_window[client]["out"] += length
                current_window[client]["protocols"][proto] += 1
            else:
                # não envolve o servidor alvo
                return
    except Exception as e:
        # não deixe a captura cair por erro num pacote
        print("Erro process_packet:", e)

def capture_loop():
    # ATENÇÃO: pyshark/tshark geralmente exige privilégios. Rode com sudo ou configure capabilities.
    cap = pyshark.LiveCapture(interface=INTERFACE, bpf_filter='')  # poderia filtrar por host SERVER_IP para economizar CPU
    for pkt in cap.sniff_continuously():
        process_packet(pkt)


def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]  # retorna o hostname
    except socket.herror:
        return ip  # se não conseguir, retorna o próprio IP
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
                "hostname": hostname,  # adicionado
                "in": v["in"],
                "out": v["out"],
                "protocols": dict(v["protocols"])
            })
        out.sort(key=lambda x: x["in"] + x["out"], reverse=True)
        return {"window_seconds": WINDOW_SECONDS, "data": out}


@app.get("/trafego/history")
def trafego_history():
    """Retorna as últimas janelas (úteis para desenhar série temporal)."""
    with _lock:
        resp = []
        for w in list(windows):
            snap = []
            for client, v in w.items():
                snap.append({
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
        v = current_window.get(client_ip)
        if not v:
            raise HTTPException(status_code=404, detail="Cliente não encontrado na janela atual")
        return {"client": client_ip, "protocols": dict(v["protocols"]), "in": v["in"], "out": v["out"]}
    
# inicialização das threads
threading.Thread(target=window_rotator, daemon=True).start()
threading.Thread(target=capture_loop, daemon=True).start()
