"""Testes para middleware de performance."""
import pytest
from fastapi.testclient import TestClient

from api.api import app
from api.auth import criar_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def token_valido():
    return criar_token({"sub": "admin"})


def test_middleware_adiciona_header_response_time(client):
    """Verifica que middleware adiciona header X-Response-Time-Ms."""
    response = client.get("/health")

    assert "X-Response-Time-Ms" in response.headers


def test_middleware_response_time_é_número_válido(client):
    """Verifica que tempo de resposta é um número positivo."""
    response = client.get("/health")

    response_time = response.headers.get("X-Response-Time-Ms")
    assert response_time is not None

    response_time_float = float(response_time)
    assert response_time_float >= 0


def test_middleware_response_time_é_razoável(client):
    """Verifica que tempo de resposta está em range esperado para /health."""
    response = client.get("/health")

    response_time = float(response.headers.get("X-Response-Time-Ms"))
    assert 0 <= response_time < 500


def test_middleware_é_adicionado_em_todas_rotas(client, token_valido):
    """Verifica que middleware é aplicado em diferentes rotas."""
    # Testa com /health (pública)
    response1 = client.get("/health")
    assert "X-Response-Time-Ms" in response1.headers

    # Testa com /auth/login (pública)
    response2 = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert "X-Response-Time-Ms" in response2.headers


def test_middleware_mede_tempo_com_precisão(client):
    """Verifica que middleware mede tempo com precisão em milissegundos."""
    response = client.get("/health")

    response_time_str = response.headers.get("X-Response-Time-Ms")
    response_time = float(response_time_str)

    assert response_time_str.count(".") == 1
    partes = response_time_str.split(".")
    if len(partes) == 2:
        casas_decimais = len(partes[1])
        assert casas_decimais <= 2
