from repositories.employee_costs_repository import RepositorioCustosFuncionariosDynamoDB


def salvar_employee_costs_dynamodb(resultado: dict) -> dict:
    """Compatibilidade com o fluxo anterior para persistir no DynamoDB."""
    repositorio = RepositorioCustosFuncionariosDynamoDB()
    return repositorio.salvar(resultado)
