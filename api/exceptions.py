from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class ArquivoInvalidoError(Exception):
    def __init__(self, nome_arquivo: str, motivo: str):
        self.nome_arquivo = nome_arquivo
        self.motivo = motivo
        super().__init__(f"Arquivo inválido '{nome_arquivo}': {motivo}")


class ExtratorError(Exception):
    def __init__(self, mensagem: str, detalhe: str = ""):
        self.detalhe = detalhe
        super().__init__(mensagem)


class RepositorioError(Exception):
    def __init__(self, operacao: str, detalhe: str = ""):
        self.operacao = operacao
        self.detalhe = detalhe
        super().__init__(f"Falha na operação '{operacao}': {detalhe}")


class ServicoExternoError(Exception):
    def __init__(self, servico: str, status_code: int, detalhe: str = ""):
        self.servico = servico
        self.status_code = status_code
        self.detalhe = detalhe
        super().__init__(f"Serviço '{servico}' retornou {status_code}: {detalhe}")


def registrar_handlers(app):
    """Registra os handlers globais de exceção no app FastAPI."""

    @app.exception_handler(ArquivoInvalidoError)
    async def handler_arquivo_invalido(request: Request, exc: ArquivoInvalidoError):
        return JSONResponse(
            status_code=422,
            content={"erro": "arquivo_invalido", "arquivo": exc.nome_arquivo, "motivo": exc.motivo},
        )

    @app.exception_handler(ExtratorError)
    async def handler_extrator(request: Request, exc: ExtratorError):
        return JSONResponse(
            status_code=500,
            content={"erro": "falha_extracao", "mensagem": str(exc), "detalhe": exc.detalhe},
        )

    @app.exception_handler(RepositorioError)
    async def handler_repositorio(request: Request, exc: RepositorioError):
        return JSONResponse(
            status_code=500,
            content={"erro": "falha_repositorio", "operacao": exc.operacao, "detalhe": exc.detalhe},
        )

    @app.exception_handler(ServicoExternoError)
    async def handler_servico_externo(request: Request, exc: ServicoExternoError):
        return JSONResponse(
            status_code=502,
            content={"erro": "servico_externo_indisponivel", "servico": exc.servico, "status_code": exc.status_code, "detalhe": exc.detalhe},
        )
