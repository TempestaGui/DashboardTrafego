#criando endpoits para Expor dados capturados do trafego de rede
# - router: Cria um router para o módulo de tráfego, prefixando todos os endpoints com /trafego.
# - trafego_current(): retorna o trafego da janela atual(ultimos window_second), se nao existir, devolve janela vazia em vez de erro
#   constroi uma lista comip do cliente, hostname, bytes recebidos (in), enviados (out) e protocolos usados e ordena os clientes por volume (in + out)
# - trafego_history(): retorna o historivo de janelas ja processado, cada janela contem timeStap(ts) e lista de clientes com trafego (in/out/protocolos)
# - trafego_drillDown(): da um foco em um ip especifico na janela atual, retornando o trafego detalhado de entrada/saida + protocolo so para esse cliente


from fastapi import APIRouter
import app.models.trafego as trafego
from app.services.dns_service import get_hostname

router = APIRouter(prefix="/trafego", tags=["Tráfego"])

@router.get("/current")
def trafego_current():
    with trafego._lock:
        if trafego.current_window is None:
            # retorna vazio, evitando 404
            return {"window_seconds": 5, "data": []}
        out = []
        for client, v in trafego.current_window.items():
            out.append({
                "client": client,
                "hostname": get_hostname(client),
                "in": v["in"],
                "out": v["out"],
                "protocols": dict(v["protocols"])
            })
        out.sort(key=lambda x: x["in"] + x["out"], reverse=True)
        return {"window_seconds": 5, "data": out}

@router.get("/history")
def trafego_history():
    with trafego._lock:
        resp = []
        for item in list(trafego.windows):
            snap = {"ts": item["ts"], "clients": []}
            for client, v in item["data"].items():
                snap["clients"].append({
                    "client": client,
                    "in": v["in"],
                    "out": v["out"],
                    "protocols": dict(v["protocols"])
                })
            resp.append(snap)
        return {"window_seconds": 5, "windows": resp}

@router.get("/drilldown/{client_ip}")
def trafego_drilldown(client_ip: str):
    with trafego._lock:
        if trafego.current_window is None:
            return {"client": client_ip, "in": 0, "out": 0, "protocols": {}}
        v = trafego.current_window.get(client_ip, {"in": 0, "out": 0, "protocols": {}})
        return {"client": client_ip, "in": v["in"], "out": v["out"], "protocols": dict(v["protocols"])}
