from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
import app.models.trafego as trafego

client = TestClient(app)

def test_trafego_current_empty():
    with trafego._lock:
        trafego.current_window = None

    response = client.get("/trafego/current")
    assert response.status_code == 200
    assert response.json() == {"window_seconds": 5, "data": []}

@patch("app.controllers.trafego_controller.get_hostname", return_value="mocked-hostname")
def test_trafego_current_with_data(mock_get_hostname):
    with trafego._lock:
        trafego.current_window = {
            "1.1.1.1": {"in": 10, "out": 5, "protocols": {"tcp": 10, "udp": 5}},
            "2.2.2.2": {"in": 3, "out": 2, "protocols": {"icmp": 5}},
        }

    response = client.get("/trafego/current")
    assert response.status_code == 200
    data = response.json()
    assert data["window_seconds"] == 5
    assert len(data["data"]) == 2
    assert data["data"][0]["client"] == "1.1.1.1"
    assert data["data"][0]["hostname"] == "mocked-hostname"
    assert data["data"][0]["in"] == 10
    assert data["data"][0]["out"] == 5
    assert isinstance(data["data"][0]["protocols"], dict)

def test_trafego_history_empty():
    with trafego._lock:
        trafego.windows = []

    response = client.get("/trafego/history")
    assert response.status_code == 200
    data = response.json()
    assert data["window_seconds"] == 5
    assert data["windows"] == []

def test_trafego_history_with_data():
    with trafego._lock:
        trafego.windows = [
            {
                "ts": 1234567890,
                "data": {
                    "1.1.1.1": {"in": 10, "out": 5, "protocols": {"tcp": 10}},
                    "2.2.2.2": {"in": 2, "out": 3, "protocols": {"udp": 5}},
                },
            },
            {
                "ts": 1234567900,
                "data": {
                    "3.3.3.3": {"in": 1, "out": 1, "protocols": {"icmp": 2}},
                },
            },
        ]

    response = client.get("/trafego/history")
    assert response.status_code == 200
    data = response.json()
    assert data["window_seconds"] == 5
    assert len(data["windows"]) == 2
    assert data["windows"][0]["ts"] == 1234567890
    assert any(client["client"] == "1.1.1.1" for client in data["windows"][0]["clients"])

def test_trafego_drilldown_no_data():
    with trafego._lock:
        trafego.current_window = None

    response = client.get("/trafego/drilldown/1.2.3.4")
    assert response.status_code == 200
    data = response.json()
    assert data == {"client": "1.2.3.4", "in": 0, "out": 0, "protocols": {}}

def test_trafego_drilldown_with_data():
    with trafego._lock:
        trafego.current_window = {
            "1.2.3.4": {"in": 100, "out": 50, "protocols": {"tcp": 100}},
        }

    response = client.get("/trafego/drilldown/1.2.3.4")
    assert response.status_code == 200
    data = response.json()
    assert data["client"] == "1.2.3.4"
    assert data["in"] == 100
    assert data["out"] == 50
    assert data["protocols"] == {"tcp": 100}

def test_trafego_drilldown_unknown_client():
    with trafego._lock:
        trafego.current_window = {
            "1.2.3.4": {"in": 100, "out": 50, "protocols": {"tcp": 100}},
        }

    response = client.get("/trafego/drilldown/9.9.9.9")
    assert response.status_code == 200
    data = response.json()
    assert data == {"client": "9.9.9.9", "in": 0, "out": 0, "protocols": {}}
