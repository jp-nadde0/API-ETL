import json
import os
import uuid
from typing import Any, Dict, Optional

import boto3

from services.interfaces import ArmazenamentoCustosFuncionarios


class RepositorioCustosFuncionariosDynamoDB(ArmazenamentoCustosFuncionarios):
    """Persiste dados de custos de funcionários no DynamoDB."""

    def __init__(self, region_name: Optional[str] = None, table_name: Optional[str] = None, endpoint_url: Optional[str] = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.table_name = table_name or os.getenv("DYNAMODB_TABLE", "employee_costs")
        self.endpoint_url = endpoint_url or os.getenv("AWS_ENDPOINT_URL")

    def salvar(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        try:
            dynamodb = boto3.resource("dynamodb", region_name=self.region_name, endpoint_url=self.endpoint_url)
            table = dynamodb.Table(self.table_name)
        except Exception as exc:
            raise RuntimeError(f"Não foi possível criar o recurso do DynamoDB: {exc}") from exc

        item = {
            "id": str(uuid.uuid4()),
            "resultado": json.dumps(resultado),
            "tipo": "employee_costs",
        }

        table.put_item(Item=item)
        return item
