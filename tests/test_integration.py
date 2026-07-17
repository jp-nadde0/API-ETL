"""Teste de Integração: Fluxo Completo da Aplicação."""
from datetime import datetime, timedelta, timezone
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from openpyxl import Workbook

from api.api import app
from api.auth import ALGORITHM, SECRET_KEY, criar_token


@pytest.fixture
def client():
    return TestClient(app)


def criar_arquivo_excel():
    """Cria um arquivo Excel com dados de vendas válidos."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Dados de Vendas"
    worksheet.append([
        "ID Venda", "Data da Venda", "Produto", "Categoria",
        "Preço Unitário", "Quantidade Vendida", "Estoque Atual"
    ])
    worksheet.append([1, "2023-01-01", "Produto A", "Categoria 1", 10.0, 5, 100])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


class TestFluxoCompleto:
    """Testes de integração do fluxo completo da aplicação."""

    def test_fluxo_login_e_extract(self, client):
        """Testa o fluxo: login → extract."""
        # 1. Login
        response_login = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response_login.status_code == 200
        token = response_login.json()["access_token"]

        # 2. Extract com token
        arquivo = criar_arquivo_excel()
        response_extract = client.post(
            "/extract_produtos/",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        assert response_extract.status_code == 200

    def test_fluxo_com_token_expirado_falha(self, client):
        """Verifica que token expirado é rejeitado."""
        # Cria token já expirado
        payload = {
            "sub": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        token_expirado = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        arquivo = criar_arquivo_excel()
        response = client.post(
            "/extract_produtos/",
            headers={"Authorization": f"Bearer {token_expirado}"},
            files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        assert response.status_code == 401


class TestHealthCheck:
    """Testes para o endpoint de health check."""

    def test_health_check_retorna_ok(self, client):
        """Verifica que /health retorna status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_check_sem_token(self, client):
        """Verifica que /health funciona sem Authorization header."""
        response = client.get("/health", headers={})
        assert response.status_code == 200


class TestDocs:
    """Testes para documentação Swagger."""

    def test_swagger_docs_é_acessível(self, client):
        """Verifica que Swagger está disponível."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_é_válido(self, client):
        """Verifica que OpenAPI schema é válido."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestMultiplasSolicitacoes:
    """Testes com múltiplas requisições para garantir estado."""

    def test_múltiplos_logins_funcionam(self, client):
        """Verifica que múltiplos logins funcionam corretamente."""
        for _ in range(3):
            response = client.post(
                "/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            assert response.status_code == 200
            assert "access_token" in response.json()

    def test_todos_os_tokens_são_válidos(self, client):
        """Verifica que todos os tokens gerados são válidos."""
        for _ in range(2):
            response_login = client.post(
                "/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            token = response_login.json()["access_token"]

            arquivo = criar_arquivo_excel()
            response = client.post(
                "/extract_produtos/",
                headers={"Authorization": f"Bearer {token}"},
                files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
            assert response.status_code == 200
