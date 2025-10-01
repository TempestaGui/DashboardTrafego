import pytest
from collections import defaultdict, deque
import _thread
import threading
import app.models.trafego as trafego

def test_new_window_returns_correct_structure():
    w = trafego.new_window()
    assert isinstance(w, defaultdict)
    val = w["some_ip"]
    assert isinstance(val, dict)
    assert val["in"] == 0
    assert val["out"] == 0
    assert isinstance(val["protocols"], defaultdict)
    # protocolos devem iniciar vazios
    assert len(val["protocols"]) == 0

def test_windows_is_deque_with_maxlen_36():
    assert isinstance(trafego.windows, deque)
    assert trafego.windows.maxlen == 36

def test_dns_cache_is_dict():
    assert isinstance(trafego._dns_cache, dict)

def test_lock_and_event_instances():
    import _thread
    assert isinstance(trafego._lock, _thread.lock)
    assert isinstance(trafego._first_window_ready, threading.Event)