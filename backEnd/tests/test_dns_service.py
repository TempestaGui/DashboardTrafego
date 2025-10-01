import pytest
from unittest.mock import patch
import app.models.trafego as trafego
from app.services import dns_service

# Teste que verifica se get_hostname retorna corretamente o hostname quando a resolução funciona
def test_get_hostname_success():
    # Limpa o cache de DNS para evitar interferência de chamadas anteriores
    trafego._dns_cache.clear()
    
    # Substitui socket.gethostbyaddr para sempre retornar um hostname fictício
    with patch("app.services.dns_service.socket.gethostbyaddr", return_value=("hostname.mock", [], [])):
        hostname = dns_service.get_hostname("8.8.8.8")
        
        # Verifica se o hostname retornado é o esperado
        assert hostname == "hostname.mock"


# Teste que verifica se get_hostname retorna o IP quando ocorre erro na resolução DNS reversa
@patch("app.services.dns_service.socket.gethostbyaddr", side_effect=Exception("Reverse DNS error"))
def test_get_hostname_failure(mock_gethostbyaddr):
    # Limpa o cache para garantir que socket.gethostbyaddr será chamado
    trafego._dns_cache.clear()
    
    hostname = dns_service.get_hostname("8.8.8.8")
    
    # Como houve erro na resolução, deve retornar o próprio IP
    assert hostname == "8.8.8.8"
