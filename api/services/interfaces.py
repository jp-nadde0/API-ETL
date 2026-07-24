from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Union


class RepositorioVendas(ABC):
    @abstractmethod
    def persistir(self, dados: List[tuple], database_url: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def consultar(self, database_url: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        raise NotImplementedError


class RepositorioResumoVendas(ABC):
    @abstractmethod
    def persistir(
        self,
        resumo: Dict[str, Any],
        database_url: Optional[str] = None,
        sheet_name: Optional[str] = None,
        data_inicial: Optional[str] = None,
        data_final: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def consultar(self, database_url: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        raise NotImplementedError


class ArmazenamentoCustosFuncionarios(ABC):
    @abstractmethod
    def salvar(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class ExtratorVendas(Protocol):
    def extrair(self, workbook_or_path: Union[object, str], sheet_name: Optional[str] = None):
        ...

    def resumir(self, workbook_or_path: Union[object, str], sheet_name: Optional[str] = None, data_inicial=None, data_final=None):
        ...
