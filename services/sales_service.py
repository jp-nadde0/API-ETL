from typing import Any, Dict, List, Optional, Union

from config.constants import SALES_SHEET_NAME
from extractors.sales_extractor import extract_produtos, resumir_vendas as resumir_vendas_extractor
from repositories.sales_repository import RepositorioVendasSqlModel
from services.interfaces import ExtratorVendas, RepositorioVendas


class AdaptadorExtratorVendas:
    """Adapta as funções de extração para o contrato do serviço."""

    def extrair(self, workbook_or_path: Union[object, str], sheet_name: Optional[str] = None):
        return extract_produtos(workbook_or_path, sheet_name)

    def resumir(self, workbook_or_path: Union[object, str], sheet_name: Optional[str] = None, data_inicial=None, data_final=None):
        return resumir_vendas_extractor(workbook_or_path, sheet_name, data_inicial, data_final)


class ServicoVendas:
    """Orquestra extração, resumo e persistência de vendas com baixo acoplamento."""

    def __init__(self, repositorio_vendas: Optional[RepositorioVendas] = None, extrator_vendas: Optional[ExtratorVendas] = None):
        self.repositorio_vendas = repositorio_vendas or RepositorioVendasSqlModel()
        self.extrator_vendas = extrator_vendas or AdaptadorExtratorVendas()

    def extrair_produtos(self, workbook_or_path: Union[object, str], sheet_name: Optional[str] = None):
        return self.extrator_vendas.extrair(workbook_or_path, sheet_name or SALES_SHEET_NAME)

    def resumir_vendas(self, workbook_or_path: Union[object, str], sheet_name: Optional[str] = None, data_inicial=None, data_final=None):
        return self.extrator_vendas.resumir(workbook_or_path, sheet_name or SALES_SHEET_NAME, data_inicial, data_final)

    def persistir_dados(self, workbook_or_path: Union[object, str], sheet_name: Optional[str] = None, database_url: Optional[str] = None) -> Dict[str, Any]:
        dados = self.extrair_produtos(workbook_or_path, sheet_name)
        return self.repositorio_vendas.persistir(dados, database_url=database_url)

    def consultar_vendas(self, database_url: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        return self.repositorio_vendas.consultar(database_url=database_url, limit=limit)
