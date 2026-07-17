import os
from typing import Optional

SALES_SHEET_NAME = "Dados de Vendas"
DEFAULT_DATABASE_URL = "sqlite:///sales.db"
DEFAULT_EXTRACTOR_URL = "http://extrator-service:5000/processar"


def obter_database_url(override: Optional[str] = None) -> str:
    """Resolve a URL do banco de dados a partir de override, variável de ambiente ou padrão."""
    return override or os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL
