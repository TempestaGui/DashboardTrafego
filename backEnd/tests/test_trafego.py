import pytest
from collections import defaultdict, deque
import _thread
import threading
import app.models.trafego as trafego

# Testa se a função new_window retorna a estrutura correta de janela de tráfego
def test_new_window_returns_correct_structure():
    w = trafego.new_window()
    assert isinstance(w, defaultdict)  # Deve ser defaultdict para criar IPs automaticamente
    val = w["some_ip"]  # Acessa um IP fictício
    assert isinstance(val, dict)  # Cada IP é um dicionário
    assert val["in"] == 0  # Tráfego de entrada inicializa em 0
    assert val["out"] == 0  # Tráfego de saída inicializa em 0
    assert isinstance(val["protocols"], defaultdict)  # Protocolos devem ser defaultdict
    assert len(val["protocols"]) == 0  # Inicialmente vazio

# Testa se a lista de janelas (windows) é um deque com tamanho máximo 36
def test_windows_is_deque_with_maxlen_36():
    assert isinstance(trafego.windows, deque)
    assert trafego.windows.maxlen == 36

# Testa se o cache DNS é um dicionário
def test_dns_cache_is_dict():
    assert isinstance(trafego._dns_cache, dict)

# Testa se lock e event estão instanciados corretamente
def test_lock_and_event_instances():
    import _thread
    assert isinstance(trafego._lock, _thread.lock)  # Lock usado para proteger acesso a current_window
    assert isinstance(trafego._first_window_ready, threading.Event)  # Event usado para sinalizar primeira janela
