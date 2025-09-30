from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.trafego_controller import router as trafego_router
from app.services.capture_service import start_capture_threads

app = FastAPI()

# CORS liberado para front-end local (Live Server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para desenvolvimento; em produção restrinja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trafego_router)

# Inicia captura em background
start_capture_threads()
