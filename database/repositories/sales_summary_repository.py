import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

from api.services.interfaces import RepositorioResumoVendas


class ResumoVenda(SQLModel, table=True):
    __tablename__ = "resumos_vendas"

    id: Optional[int] = Field(default=None, primary_key=True)
    sheet_name: Optional[str] = None
    data_inicial: Optional[str] = None
    data_final: Optional[str] = None
    resumo_json: str
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sheet_name": self.sheet_name,
            "data_inicial": self.data_inicial,
            "data_final": self.data_final,
            "resumo": json.loads(self.resumo_json),
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }


class RepositorioResumoVendasSqlModel(RepositorioResumoVendas):
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url

    def _obter_engine(self):
        resolved_url = self.database_url or os.getenv("DATABASE_URL") or os.getenv("RDS_DATABASE_URL") or "sqlite:///sales.db"
        return create_engine(resolved_url, echo=False)

    def persistir(
        self,
        resumo: Dict[str, Any],
        database_url: Optional[str] = None,
        sheet_name: Optional[str] = None,
        data_inicial: Optional[str] = None,
        data_final: Optional[str] = None,
    ) -> Dict[str, Any]:
        engine = self._obter_engine() if database_url is None else create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(engine)

        registro = ResumoVenda(
            sheet_name=sheet_name,
            data_inicial=data_inicial,
            data_final=data_final,
            resumo_json=json.dumps(resumo, ensure_ascii=False),
        )

        with Session(engine) as session:
            session.add(registro)
            session.commit()
            session.refresh(registro)

        return {"persistidos": 1, "database_url": engine.url.render_as_string(hide_password=False), "resumo": registro.to_dict()}

    def consultar(self, database_url: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        engine = self._obter_engine() if database_url is None else create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            statement = select(ResumoVenda).order_by(ResumoVenda.id.desc()).limit(limit)
            resumos = session.exec(statement).all()

        return [resumo.to_dict() for resumo in resumos]