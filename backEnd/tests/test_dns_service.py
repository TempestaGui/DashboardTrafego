import pytest
from unittest.mock import patch
import app.models.trafego as trafego
from app.services import dns_service

def test_get_hostname_success():
    # Limpa o cache para evitar interferência
    trafego._dns_cache.clear()
    
    with patch("app.services.dns_service.socket.gethostbyaddr", return_value=("hostname.mock", [], [])):
        hostname = dns_service.get_hostname("8.8.8.8")
        assert hostname == "hostname.mock"

@patch("app.services.dns_service.socket.gethostbyaddr", side_effect=Exception("Reverse DNS error"))
def test_get_hostname_failure(mock_gethostbyaddr):
    # Limpa o cache para garantir que socket.gethostbyaddr será chamado
    trafego._dns_cache.clear()
    
    hostname = dns_service.get_hostname("8.8.8.8")
    assert hostname == "8.8.8.8"  # retorna o IP se não conseguir resolver
