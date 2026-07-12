import os
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from config.constants import DEFAULT_EXTRACTOR_URL, SALES_SHEET_NAME
from repositories.employee_costs_repository import RepositorioCustosFuncionariosDynamoDB
from services.employee_costs_service import ServicoCustosFuncionarios
from services.file_service import ServicoArquivoTemporario
from services.sales_service import ServicoVendas

app = FastAPI()

servico_arquivo = ServicoArquivoTemporario()
servico_vendas = ServicoVendas()
servico_custos_funcionarios = ServicoCustosFuncionarios(armazenamento=RepositorioCustosFuncionariosDynamoDB())

@app.post("/extract_produtos/")
async def extract_produtos_endpoint(file: UploadFile = File(...)):
    """Endpoint para extrair produtos de um arquivo Excel (.xlsx)."""
    temp_file_path = servico_arquivo.salvar(file)
    try:
        produtos = servico_vendas.extrair_produtos(temp_file_path, sheet_name=SALES_SHEET_NAME)
        return {"produtos": produtos}
    finally:
        servico_arquivo.remover(temp_file_path)

@app.post("/resumir_vendas/")
async def resumir_vendas_endpoint(file: UploadFile = File(...)):
    """Endpoint para resumir vendas de um arquivo Excel (.xlsx)."""
    temp_file_path = servico_arquivo.salvar(file)
    try:
        resumo = servico_vendas.resumir_vendas(temp_file_path, sheet_name=SALES_SHEET_NAME)
        return {"resumo": resumo}
    finally:
        servico_arquivo.remover(temp_file_path)


@app.post("/vendas/persistir/")
async def persistir_vendas_endpoint(file: UploadFile = File(...), database_url: Optional[str] = Query(default=None)):
    """Recebe um arquivo .xlsx, envia ao serviço de extração e retorna os dados em JSON."""
    temp_file_path = servico_arquivo.salvar(file)
    try:
        resolved_database_url = database_url or os.getenv("DATABASE_URL")
        extractor_url = os.getenv("EXTRACTOR_URL", DEFAULT_EXTRACTOR_URL)
        with open(temp_file_path, "rb") as upload_handle:
            response = requests.post(
                extractor_url,
                files={"file": (file.filename, upload_handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                timeout=60,
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        payload = response.json()
        registros = servico_vendas.consultar_vendas(database_url=resolved_database_url)
        return {
            "resultado": payload,
            "vendas": registros,
        }
    finally:
        servico_arquivo.remover(temp_file_path)


@app.post("/extract_employee_costs/")
async def extract_employee_costs_endpoint(file: UploadFile = File(...)):
    """Endpoint para extrair custos de funcionários de um arquivo PDF."""
    temp_file_path = servico_arquivo.salvar(file)
    try:
        resultado = servico_custos_funcionarios.extrair_e_persistir(temp_file_path)
        return resultado
    finally:
        servico_arquivo.remover(temp_file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)