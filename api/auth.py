import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "troque-esta-chave-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

security = HTTPBearer()


def criar_token(dados: dict, expiracao_horas: int = ACCESS_TOKEN_EXPIRE_HOURS) -> str:
    payload = dados.copy()
    expira = datetime.now(timezone.utc) + timedelta(hours=expiracao_horas)
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
