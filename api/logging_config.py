import logging
import sys


def configurar_logging():
    """Configura logging estruturado para toda a aplicação."""
    formato = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formato)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if not root.handlers:
        root.addHandler(handler)

    # Silencia logs verbose de libs externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def obter_logger(nome: str) -> logging.Logger:
    return logging.getLogger(nome)
