from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from capture import traffic_data, start_capture
import threading

app = FastAPI()

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # permite todas as origens (pode restringir depois)
    allow_credentials=True,
    allow_methods=["*"],  # permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # permite todos os headers
)

@app.get("/traffic")
def get_traffic():
    return traffic_data

@app.get("/traffic/{client_ip}")
def get_client(client_ip: str):
    return traffic_data.get(client_ip, {"in": 0, "out": 0, "protocols": {}})

# Inicia captura em paralelo
threading.Thread(target=start_capture, daemon=True).start()
