"""Testes para exceções customizadas."""
import pytest
from fastapi.testclient import TestClient

from api.api import app
from api.auth import criar_token
from api.exceptions import (
    ArquivoInvalidoError,
    ExtratorError,
    RepositorioError,
    ServicoExternoError,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def token_valido():
    return criar_token({"sub": "admin"})


# ────────────────────────────────────────────────────────────────────────────
# Testes de exceções diretas
# ────────────────────────────────────────────────────────────────────────────

def test_arquivo_invalido_error_inicializa():
    """Verifica que ArquivoInvalidoError inicializa corretamente."""
    exc = ArquivoInvalidoError("arquivo.pdf", "formato esperado: xlsx")

    assert exc.nome_arquivo == "arquivo.pdf"
    assert exc.motivo == "formato esperado: xlsx"
    assert "arquivo.pdf" in str(exc)


def test_extrator_error_inicializa():
    """Verifica que ExtratorError inicializa corretamente."""
    exc = ExtratorError("Falha ao extrair", "Coluna 'Produto' não encontrada")

    assert exc.detalhe == "Coluna 'Produto' não encontrada"
    assert "Falha ao extrair" in str(exc)


def test_repositorio_error_inicializa():
    """Verifica que RepositorioError inicializa corretamente."""
    exc = RepositorioError("INSERT", "Violação de chave primária")

    assert exc.operacao == "INSERT"
    assert exc.detalhe == "Violação de chave primária"


def test_servico_externo_error_inicializa():
    """Verifica que ServicoExternoError inicializa corretamente."""
    exc = ServicoExternoError("extrator-service", 502, "Connection timeout")

    assert exc.servico == "extrator-service"
    assert exc.status_code == 502
    assert exc.detalhe == "Connection timeout"


# ────────────────────────────────────────────────────────────────────────────
# Testes de handlers de exceção na API
# ────────────────────────────────────────────────────────────────────────────

def test_arquivo_invalido_error_retorna_422(client, token_valido):
    """Verifica que ArquivoInvalidoError retorna status 422."""
    from io import BytesIO

    # Arquivo fake com extensão PDF
    pdf_fake = BytesIO(b"%PDF-fake")

    response = client.post(
        "/extract_produtos/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("documento.pdf", pdf_fake, "application/pdf")}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["erro"] == "arquivo_invalido"
    assert "arquivo" in data
    assert "motivo" in data


def test_arquivo_invalido_retorna_json_estruturado(client, token_valido):
    """Verifica que resposta tem estrutura esperada."""
    from io import BytesIO

    pdf_fake = BytesIO(b"%PDF-fake")

    response = client.post(
        "/extract_produtos/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("teste.pdf", pdf_fake, "application/pdf")}
    )

    data = response.json()
    assert "erro" in data
    assert "arquivo" in data
    assert "motivo" in data
    assert data["arquivo"] == "teste.pdf"


def test_extrator_error_lança_exceção_corretamente():
    """Verifica que ExtratorError pode ser lançado e capturado."""
    try:
        raise ExtratorError("Erro na extração", "Workbook inválido")
    except ExtratorError as e:
        assert "Erro na extração" in str(e)
        assert e.detalhe == "Workbook inválido"


def test_repositorio_error_lança_exceção_corretamente():
    """Verifica que RepositorioError pode ser lançado e capturado."""
    try:
        raise RepositorioError("UPDATE", "Nenhuma linha afetada")
    except RepositorioError as e:
        assert e.operacao == "UPDATE"
        assert "Nenhuma linha afetada" in e.detalhe


def test_servico_externo_error_lança_exceção_corretamente():
    """Verifica que ServicoExternoError pode ser lançado e capturado."""
    try:
        raise ServicoExternoError("api-externa", 500, "Internal server error")
    except ServicoExternoError as e:
        assert e.servico == "api-externa"
        assert e.status_code == 500


# ────────────────────────────────────────────────────────────────────────────
# Testes de validação de formato de arquivo
# ────────────────────────────────────────────────────────────────────────────

def test_extract_employee_costs_rejeita_arquivo_excel(client, token_valido):
    """Verifica que /extract_employee_costs/ rejeita .xlsx."""
    from io import BytesIO
    from openpyxl import Workbook

    wb = Workbook()
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = client.post(
        "/extract_employee_costs/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("dados.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )

    assert response.status_code == 422
    assert response.json()["erro"] == "arquivo_invalido"
    assert "formato deve ser .pdf" in response.json()["motivo"]


def test_extract_employee_costs_rejeita_arquivo_txt(client, token_valido):
    """Verifica que /extract_employee_costs/ rejeita .txt."""
    from io import BytesIO

    txt_content = BytesIO(b"conteudo em texto")

    response = client.post(
        "/extract_employee_costs/",
        headers={"Authorization": f"Bearer {token_valido}"},
        files={"file": ("dados.txt", txt_content, "text/plain")}
    )

    assert response.status_code == 422
