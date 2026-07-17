"""Testes dos endpoints da API com autenticação e validação."""
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from api.api import USUARIOS, app, criar_token


@pytest.fixture
def client():
    """Fixture com TestClient da aplicação."""
    return TestClient(app)


@pytest.fixture
def token_valido():
    """Fixture que retorna um token JWT válido."""
    return criar_token({"sub": "admin"})


def criar_arquivo_excel():
    """Função que cria um novo arquivo Excel para testes."""
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


# ────────────────────────────────────────────────────────────────────────────
# Testes de autenticação
# ────────────────────────────────────────────────────────────────────────────

def test_login_com_credenciais_corretas(client):
    """Verifica login com usuário e senha válidos."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_com_usuario_invalido(client):
    """Verifica que login falha com usuário inexistente."""
    response = client.post(
        "/auth/login",
        json={"username": "usuario_inexistente", "password": "senha"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


def test_login_com_senha_incorreta(client):
    """Verifica que login falha com senha errada."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "senha_errada"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


# ────────────────────────────────────────────────────────────────────────────
# Testes de endpoints protegidos
# ────────────────────────────────────────────────────────────────────────────

def test_extract_produtos_sem_token_retorna_403(client):
    """Verifica que endpoint protegido rejeita requisição sem token."""
    arquivo = criar_arquivo_excel()
    response = client.post(
        "/extract_produtos/",
        files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 401


def test_extract_produtos_com_token_invalido_retorna_401(client):
    """Verifica que token inválido é rejeitado."""
    arquivo = criar_arquivo_excel()
    response = client.post(
        "/extract_produtos/",
        headers={"Authorization": "Bearer token_invalido"},
        files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 401


def test_extract_produtos_com_arquivo_pdf_retorna_422(client, token_valido):
    """Verifica que arquivo em formato errado é rejeitado."""
    pdf_fake = BytesIO(b"%PDF-1.4\n%fake pdf content")

    response = client.post(
        "/extract_produtos/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("documento.pdf", pdf_fake, "application/pdf")}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["erro"] == "arquivo_invalido"
    assert "formato deve ser .xlsx" in data["motivo"]


def test_extract_produtos_com_token_valido_e_arquivo_valido(client, token_valido):
    """Verifica que endpoint funciona com token válido e arquivo correto."""
    arquivo = criar_arquivo_excel()
    response = client.post(
        "/extract_produtos/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "produtos" in data


def test_resumir_vendas_sem_token_retorna_403(client):
    """Verifica que /resumir_vendas/ também é protegido."""
    arquivo = criar_arquivo_excel()
    response = client.post(
        "/resumir_vendas/",
        files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 401


# ────────────────────────────────────────────────────────────────────────────
# Testes de endpoints públicos
# ────────────────────────────────────────────────────────────────────────────

def test_health_check_sem_autenticacao(client):
    """Verifica que /health é público."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_docs_sem_autenticacao(client):
    """Verifica que Swagger /docs é acessível."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


# ────────────────────────────────────────────────────────────────────────────
# Testes de headers e respostas
# ────────────────────────────────────────────────────────────────────────────

def test_response_time_header_adicionado(client, token_valido):
    """Verifica que response time header é adicionado."""
    arquivo = criar_arquivo_excel()
    response = client.post(
        "/extract_produtos/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("vendas.xlsx", arquivo, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert "X-Response-Time-Ms" in response.headers
    response_time = float(response.headers["X-Response-Time-Ms"])
    assert response_time > 0


def test_login_retorna_token_type_bearer(client):
    """Verifica que login retorna token_type correto."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"}
    )

    data = response.json()
    assert data["token_type"] == "bearer"


def test_extract_employee_costs_com_arquivo_excel_retorna_422(client, token_valido):
    """Verifica que /extract_employee_costs/ rejeita arquivos que não são PDF."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["col1", "col2"])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = client.post(
        "/extract_employee_costs/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("dados.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 422
    assert response.json()["erro"] == "arquivo_invalido"
