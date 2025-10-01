import pytest
from unittest.mock import patch, MagicMock
from app.services import capture_service
import app.models.trafego as trafego

# Teste que verifica se process_packet funciona corretamente quando o pacote possui camada IP
def test_process_packet_with_ip():
    # Garante que exista uma janela atual de tráfego para armazenar os dados
    with trafego._lock:
        trafego.current_window = trafego.new_window()

    # Cria um pacote fictício (mock) com IP de origem e destino
    pkt = MagicMock()
    pkt.ip.src = "10.0.0.1"
    pkt.ip.dst = "10.0.0.2"
    pkt.ip.__bool__.return_value = True  # Simula que o pacote possui IP

    # Substitui a função proto_of_packet para sempre retornar "TCP"
    with patch("app.services.capture_service.proto_of_packet", return_value="TCP"):
        result = capture_service.process_packet(pkt)  # Processa o pacote

    # Garante que a função não retorna nada (processamento interno apenas)
    assert result is None

    # Verifica se os IPs foram adicionados corretamente na janela de tráfego
    with trafego._lock:
        _ = trafego.current_window["10.0.0.1"]
        _ = trafego.current_window["10.0.0.2"]

        assert "10.0.0.1" in trafego.current_window
        assert "10.0.0.2" in trafego.current_window

        # Confirma que o campo de protocolos foi inicializado como dicionário
        assert isinstance(trafego.current_window["10.0.0.1"]["protocols"], dict)


# Teste que verifica se process_packet ignora pacotes sem camada IP
def test_process_packet_no_ip():
    pkt = MagicMock()
    del pkt.ip  # Remove a camada IP do pacote mock

    result = capture_service.process_packet(pkt)  # Processa o pacote

    # Como o pacote não possui IP, a função deve retornar None
    assert result is None
