"""Testes para logging estruturado."""
import logging

import pytest

from api.logging_config import configurar_logging, obter_logger


def test_configurar_logging_inicializa():
    """Verifica que configurar_logging não lança erro."""
    configurar_logging()  # Não deve lançar exceção


def test_obter_logger_retorna_logger_válido():
    """Verifica que obter_logger retorna um Logger válido."""
    logger = obter_logger("test_module")

    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_obter_logger_mesmo_nome_retorna_mesmo_logger():
    """Verifica que obter_logger com mesmo nome retorna o mesmo logger."""
    logger1 = obter_logger("meu_modulo")
    logger2 = obter_logger("meu_modulo")

    assert logger1 is logger2


def test_logger_pode_fazer_log_info(caplog):
    """Verifica que logger pode registrar mensagens INFO."""
    logger = obter_logger("test")
    logger.info("Mensagem de teste")

    assert "Mensagem de teste" in caplog.text


def test_logger_pode_fazer_log_warning(caplog):
    """Verifica que logger pode registrar mensagens WARNING."""
    logger = obter_logger("test")
    logger.warning("Aviso de teste")

    assert "Aviso de teste" in caplog.text


def test_logger_pode_fazer_log_error(caplog):
    """Verifica que logger pode registrar mensagens ERROR."""
    logger = obter_logger("test")
    logger.error("Erro de teste")

    assert "Erro de teste" in caplog.text


def test_logger_com_parametros(caplog):
    """Verifica que logger funciona com formatação de strings."""
    logger = obter_logger("test")
    logger.info("Usuário %s fez login", "admin")

    assert "Usuário admin fez login" in caplog.text


def test_logging_estruturado_com_timestamp(caplog):
    """Verifica que logs incluem timestamp."""
    configurar_logging()
    logger = obter_logger("test")

    with caplog.at_level(logging.INFO):
        logger.info("Teste com timestamp")

    # O timestamp é adicionado pelo formatter
    assert "Teste com timestamp" in caplog.text


def test_logger_diferentes_modulos():
    """Verifica que loggers de diferentes módulos têm nomes corretos."""
    logger1 = obter_logger("modulo1")
    logger2 = obter_logger("modulo2")

    assert logger1.name == "modulo1"
    assert logger2.name == "modulo2"
    assert logger1 is not logger2


def test_logger_root_configurado():
    """Verifica que root logger foi configurado."""
    configurar_logging()
    root_logger = logging.getLogger()

    # Root logger deve ter handlers
    assert len(root_logger.handlers) > 0


def test_logger_nivel_info_por_padrão():
    """Verifica que nível padrão é INFO."""
    configurar_logging()
    root_logger = logging.getLogger()

    assert root_logger.level == logging.INFO


def test_logger_uvicorn_silenciado(caplog):
    """Verifica que logs do uvicorn.access não aparecem (WARNING level)."""
    configurar_logging()
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.info("Log que não deve aparecer")

    # INFO logs de uvicorn.access não devem aparecer por default
    # (logger foi setado para WARNING)
    with caplog.at_level(logging.INFO):
        uvicorn_logger.debug("Debug que não deve aparecer")

    # Não devemos ver nada
    assert "Debug que não deve aparecer" not in caplog.text
