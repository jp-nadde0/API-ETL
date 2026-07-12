import os

import uvicorn
from fastapi import FastAPI, File, UploadFile

from config.constants import SALES_SHEET_NAME
from services.file_service import ServicoArquivoTemporario
from services.sales_service import ServicoVendas

app = FastAPI(title="Extrator de vendas")

servico_arquivo = ServicoArquivoTemporario()
servico_vendas = ServicoVendas()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/processar")
async def processar_planilha(file: UploadFile = File(...)):
    """Recebe um arquivo Excel, salva em /tmp e persiste os dados no banco configurado."""
    temp_file_path = servico_arquivo.salvar(file)
    try:
        resultado = servico_vendas.persistir_dados(
            temp_file_path,
            sheet_name=SALES_SHEET_NAME,
            database_url=os.getenv("DATABASE_URL"),
        )
        return {
            "status": "ok",
            "arquivo": file.filename,
            **resultado,
        }
    except Exception as exc:
        raise RuntimeError(f"Erro ao processar a planilha: {exc}") from exc
    finally:
        servico_arquivo.remover(temp_file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
