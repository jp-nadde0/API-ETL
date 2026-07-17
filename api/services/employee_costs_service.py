from typing import Any, Dict, Optional

from extractors.employee_costs_extractor import ExtratorPDF
from repositories.employee_costs_repository import RepositorioCustosFuncionariosDynamoDB
from services.interfaces import ArmazenamentoCustosFuncionarios


class ServicoCustosFuncionarios:
    """Responsável por orquestrar extração e persistência de custos de funcionários."""

    def __init__(self, extrator_pdf: Optional[ExtratorPDF] = None, armazenamento: Optional[ArmazenamentoCustosFuncionarios] = None):
        self.extrator_pdf = extrator_pdf or ExtratorPDF()
        self.armazenamento = armazenamento or RepositorioCustosFuncionariosDynamoDB()

    def extrair_e_persistir(self, caminho_pdf: str) -> Dict[str, Any]:
        resultado = self.extrator_pdf.extrair_dados(caminho_pdf)
        item_salvo = self.armazenamento.salvar(resultado)
        return {"resultado": resultado, "dynamo_item": item_salvo}
