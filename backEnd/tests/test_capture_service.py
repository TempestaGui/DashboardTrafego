import pytest
from unittest.mock import patch, MagicMock
from app.services import capture_service
import app.models.trafego as trafego

def test_process_packet_with_ip():
    # garante que current_window existe
    with trafego._lock:
        trafego.current_window = trafego.new_window()

    pkt = MagicMock()
    pkt.ip.src = "10.0.0.1"
    pkt.ip.dst = "10.0.0.2"
    pkt.ip.__bool__.return_value = True

    with patch("app.services.capture_service.proto_of_packet", return_value="TCP"):
        result = capture_service.process_packet(pkt)

    assert result is None

    with trafego._lock:
        _ = trafego.current_window["10.0.0.1"]
        _ = trafego.current_window["10.0.0.2"]

        assert "10.0.0.1" in trafego.current_window
        assert "10.0.0.2" in trafego.current_window

        assert isinstance(trafego.current_window["10.0.0.1"]["protocols"], dict)

def test_process_packet_no_ip():
    pkt = MagicMock()
    del pkt.ip
    result = capture_service.process_packet(pkt)
    assert result is None
