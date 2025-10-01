import threading, time
import pyshark
import asyncio
import app.models.trafego as trafego
from app.utils.protocols import proto_of_packet
from app.config import SERVER_IP, INTERFACE, WINDOW_SECONDS

def process_packet(pkt):
    try:
        ip = getattr(pkt, "ip", None) or getattr(pkt, "ipv6", None)
        if ip is None:
            return
        src, dst = getattr(ip, "src", ""), getattr(ip, "dst", "")
        try:
            length = int(getattr(pkt, "length", 0))
        except:
            length = 0
        proto = proto_of_packet(pkt)

        with trafego._lock:
            if trafego.current_window is None:
                return
            if dst == SERVER_IP and src:
                client = src
                trafego.current_window[client]["in"] += length
                trafego.current_window[client]["protocols"][proto] += length
            elif src == SERVER_IP and dst:
                client = dst
                trafego.current_window[client]["out"] += length
                trafego.current_window[client]["protocols"][proto] += length

    except Exception as e:
        print("Erro process_packet:", e)


def window_rotator():
    while True:
        with trafego._lock:
            w = trafego.new_window()
            trafego.windows.append({"ts": int(time.time()), "data": w})
            trafego.current_window = w
            trafego._first_window_ready.set()
        time.sleep(WINDOW_SECONDS)


def capture_loop():
    trafego._first_window_ready.wait()
    bpf = f'host {SERVER_IP}'
    while True:
        try:
            # cria um event loop para esta thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            cap = pyshark.LiveCapture(interface=INTERFACE, bpf_filter=bpf)
            for pkt in cap.sniff_continuously():
                process_packet(pkt)

        except Exception as e:
            print("Capture erro:", e)
            time.sleep(2)

def start_capture_threads():
    threading.Thread(target=window_rotator, daemon=True).start()
    threading.Thread(target=capture_loop, daemon=True).start()
