import os
from typing import Any, Dict, List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

from api.services.interfaces import RepositorioVendas


class Venda(SQLModel, table=True):
    __tablename__ = 'vendas'

    id: Optional[int] = Field(default=None, primary_key=True)
    id_venda: int
    data_venda: Optional[str] = None
    produto: str
    categoria: Optional[str] = None
    preco_unitario: float
    quantidade_vendida: float
    faturamento_total: float
    estoque_atual: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'id_venda': self.id_venda,
            'data_venda': self.data_venda,
            'produto': self.produto,
            'categoria': self.categoria,
            'preco_unitario': self.preco_unitario,
            'quantidade_vendida': self.quantidade_vendida,
            'faturamento_total': self.faturamento_total,
            'estoque_atual': self.estoque_atual,
        }


class RepositorioVendasSqlModel(RepositorioVendas):
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url

    def _obter_engine(self):
        resolved_url = self.database_url or os.getenv('DATABASE_URL') or os.getenv('RDS_DATABASE_URL') or 'sqlite:///sales.db'
        return create_engine(resolved_url, echo=False)

    def persistir(self, dados: List[tuple], database_url: Optional[str] = None) -> Dict[str, Any]:
        engine = self._obter_engine() if database_url is None else create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            for item in dados:
                id_venda, data_venda, produto, categoria, preco_unitario, quantidade_vendida, faturamento_total, estoque_atual = item
                venda = Venda(
                    id_venda=int(id_venda) if id_venda is not None else 0,
                    data_venda=data_venda,
                    produto=str(produto),
                    categoria=str(categoria) if categoria is not None else None,
                    preco_unitario=float(preco_unitario),
                    quantidade_vendida=float(quantidade_vendida),
                    faturamento_total=float(faturamento_total),
                    estoque_atual=float(estoque_atual) if estoque_atual is not None else None,
                )
                session.add(venda)
            session.commit()

        return {'persistidos': len(dados), 'database_url': engine.url.render_as_string(hide_password=False)}

    def consultar(self, database_url: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        engine = self._obter_engine() if database_url is None else create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            statement = select(Venda).order_by(Venda.id).limit(limit)
            vendas = session.exec(statement).all()

        return [venda.to_dict() for venda in vendas]
