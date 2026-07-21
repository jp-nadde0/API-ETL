import os
import time
from typing import List, Optional

import requests
import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel

from api.auth import criar_token, verificar_token
from api.exceptions import ArquivoInvalidoError, ServicoExternoError, registrar_handlers
from api.logging_config import configurar_logging, obter_logger
from config.constants import DEFAULT_EXTRACTOR_URL, SALES_SHEET_NAME, obter_database_url
from database.repositories.employee_costs_repository import RepositorioCustosFuncionariosDynamoDB
from services.employee_costs_service import ServicoCustosFuncionarios
from services.file_service import ServicoArquivoTemporario
from services.sales_service import ServicoVendas

configurar_logging()
logger = obter_logger(__name__)

app = FastAPI(
    title="API ETL",
    description="API para extração e persistência de dados de vendas e custos de funcionários.",
    version="1.0.0",
)

registrar_handlers(app)

# Em produção, substitua por consulta ao banco com senhas hasheadas
USUARIOS = {
    os.getenv("API_USERNAME", "admin"): os.getenv("API_PASSWORD", "admin123"),
}

servico_arquivo = ServicoArquivoTemporario()
servico_vendas = ServicoVendas()
servico_custos_funcionarios = ServicoCustosFuncionarios(armazenamento=RepositorioCustosFuncionariosDynamoDB())


# ── Middleware de métricas de performance ────────────────────────────────────

@app.middleware("http")
async def middleware_metricas(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    response.headers["X-Response-Time-Ms"] = str(duracao_ms)
    logger.info("%s %s → %s | %sms", request.method, request.url.path, response.status_code, duracao_ms)
    return response


# ── Modelos Pydantic ─────────────────────────────────────────────────────────

class CredenciaisLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ProdutosResponse(BaseModel):
    produtos: List[dict]


class ResumoResponse(BaseModel):
    resumo: List[dict]


class VendasPersistirResponse(BaseModel):
    resultado: dict
    vendas: List[dict]


class CustosResponse(BaseModel):
    resultado: dict
    dynamo_item: dict


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(credenciais: CredenciaisLogin):
    """Autentica o usuário e retorna um JWT válido por 8 horas."""
    senha_correta = USUARIOS.get(credenciais.username)
    if not senha_correta or credenciais.password != senha_correta:
        logger.warning("Tentativa de login inválida para usuário '%s'", credenciais.username)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token({"sub": credenciais.username})
    logger.info("Login bem-sucedido para usuário '%s'", credenciais.username)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/extract_produtos/", tags=["vendas"])
async def extract_produtos_endpoint(file: UploadFile = File(...), _: dict = Depends(verificar_token)):
    """Extrai produtos de um arquivo Excel (.xlsx)."""
    if not file.filename.endswith(".xlsx"):
        raise ArquivoInvalidoError(file.filename, "formato deve ser .xlsx")
    logger.info("Extraindo produtos de '%s'", file.filename)
    with servico_arquivo.arquivo_temporario(file) as temp_path:
        return {"produtos": servico_vendas.extrair_produtos(temp_path, sheet_name=SALES_SHEET_NAME)}


@app.post("/resumir_vendas/", tags=["vendas"])
async def resumir_vendas_endpoint(file: UploadFile = File(...), _: dict = Depends(verificar_token)):
    """Resume vendas de um arquivo Excel (.xlsx)."""
    if not file.filename.endswith(".xlsx"):
        raise ArquivoInvalidoError(file.filename, "formato deve ser .xlsx")
    logger.info("Resumindo vendas de '%s'", file.filename)
    with servico_arquivo.arquivo_temporario(file) as temp_path:
        return {"resumo": servico_vendas.resumir_vendas(temp_path, sheet_name=SALES_SHEET_NAME)}


@app.post("/vendas/persistir/", tags=["vendas"])
async def persistir_vendas_endpoint(
    file: UploadFile = File(...),
    database_url: Optional[str] = Query(default=None),
    _: dict = Depends(verificar_token),
):
    """Recebe um arquivo .xlsx, envia ao serviço de extração e persiste no banco."""
    if not file.filename.endswith(".xlsx"):
        raise ArquivoInvalidoError(file.filename, "formato deve ser .xlsx")

    resolved_database_url = obter_database_url(database_url)
    extractor_url = os.getenv("EXTRACTOR_URL", DEFAULT_EXTRACTOR_URL)
    logger.info("Persistindo vendas de '%s' via extrator '%s'", file.filename, extractor_url)

    with servico_arquivo.arquivo_temporario(file) as temp_path:
        with open(temp_path, "rb") as upload_handle:
            response = requests.post(
                extractor_url,
                files={"file": (file.filename, upload_handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                timeout=60,
            )

        if response.status_code != 200:
            raise ServicoExternoError("extrator-service", response.status_code, response.text)

        return {
            "resultado": response.json(),
            "vendas": servico_vendas.consultar_vendas(database_url=resolved_database_url),
        }


@app.post("/extract_employee_costs/", tags=["custos"])
async def extract_employee_costs_endpoint(file: UploadFile = File(...), _: dict = Depends(verificar_token)):
    """Extrai custos de funcionários de um arquivo PDF e persiste no DynamoDB."""
    if not file.filename.endswith(".pdf"):
        raise ArquivoInvalidoError(file.filename, "formato deve ser .pdf")
    logger.info("Extraindo custos de funcionários de '%s'", file.filename)
    with servico_arquivo.arquivo_temporario(file, suffix=".pdf") as temp_path:
        return servico_custos_funcionarios.extrair_e_persistir(temp_path)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)