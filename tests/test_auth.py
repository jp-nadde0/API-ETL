"""Testes para o módulo de autenticação JWT."""
from datetime import datetime, timedelta, timezone

import pytest
from jose import JWTError, jwt

from api.auth import ACCESS_TOKEN_EXPIRE_HOURS, ALGORITHM, SECRET_KEY, criar_token, verificar_token
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


def test_criar_token_com_dados_validos():
    """Verifica se criar_token gera um JWT válido."""
    dados = {"sub": "usuario_teste"}
    token = criar_token(dados)

    assert token is not None
    assert isinstance(token, str)

    # Decodifica e valida
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "usuario_teste"
    assert "exp" in payload


def test_criar_token_contém_expiração():
    """Verifica se o token tem expiração configurada."""
    dados = {"sub": "teste"}
    token = criar_token(dados, expiracao_horas=2)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    agora = datetime.now(timezone.utc)
    exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    # Token deve expirar em ~2 horas
    diferenca = (exp_datetime - agora).total_seconds() / 3600
    assert 1.9 < diferenca < 2.1


def test_criar_token_com_expiração_padrão():
    """Verifica a expiração padrão de 8 horas."""
    dados = {"sub": "teste"}
    token = criar_token(dados)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    agora = datetime.now(timezone.utc)
    exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    diferenca = (exp_datetime - agora).total_seconds() / 3600
    assert 7.9 < diferenca < 8.1


def test_verificar_token_valido_retorna_payload():
    """Verifica se token válido retorna o payload corretamente."""
    dados = {"sub": "usuario_teste"}
    token = criar_token(dados)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    payload = verificar_token(credentials)

    assert payload["sub"] == "usuario_teste"


def test_verificar_token_inválido_lança_exceção():
    """Verifica se token inválido lança HTTPException com 401."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token_inválido_aleatorio")

    with pytest.raises(HTTPException) as exc_info:
        verificar_token(credentials)

    assert exc_info.value.status_code == 401
    assert "inválido ou expirado" in exc_info.value.detail


def test_verificar_token_expirado_lança_exceção():
    """Verifica se token expirado é rejeitado."""
    # Cria token que expira em -1 hora
    payload = {
        "sub": "teste",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1)
    }
    token_expirado = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_expirado)

    with pytest.raises(HTTPException) as exc_info:
        verificar_token(credentials)

    assert exc_info.value.status_code == 401


def test_verificar_token_com_secret_incorreto_falha():
    """Verifica que token assinado com chave errada é rejeitado."""
    dados = {"sub": "teste"}
    token_invalido = jwt.encode(dados, "chave_errada", algorithm=ALGORITHM)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_invalido)

    with pytest.raises(HTTPException) as exc_info:
        verificar_token(credentials)

    assert exc_info.value.status_code == 401
