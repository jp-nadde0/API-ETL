import os
import tempfile
from typing import Optional

from fastapi import HTTPException, UploadFile


class ServicoArquivoTemporario:
    """Responsável por salvar e remover arquivos enviados pelo cliente."""

    def salvar(self, upload_file: UploadFile, suffix: Optional[str] = None) -> str:
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Arquivo sem nome")

        resolved_suffix = suffix or os.path.splitext(upload_file.filename)[1] or ".xlsx"
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=resolved_suffix) as temp_file:
                contents = upload_file.file.read()
                temp_file.write(contents)
                return temp_file.name
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar o arquivo: {exc}") from exc

    def remover(self, file_path: Optional[str]) -> None:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
