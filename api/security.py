"""Utilitarios de autenticacao JWT para a Deep Agent API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import yaml
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from deep_agent.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas


def _load_users() -> dict:
    """Carrega credenciais do AUTH_CONFIG_YAML."""
    if not settings.auth_config_yaml:
        return {}
    try:
        config = yaml.safe_load(settings.auth_config_yaml)
        return config.get("credentials", {}).get("usernames", {})
    except Exception:
        return {}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Verifica username + senha e retorna dados do usuario ou None."""
    users = _load_users()
    user = users.get(username)
    if not user:
        return None
    if not pwd_context.verify(password, user.get("password", "")):
        return None
    return {
        "username": username,
        "name": user.get("name", username),
        "email": user.get("email", ""),
        "roles": user.get("roles", []),
    }


def create_access_token(data: dict) -> str:
    """Gera JWT com expiracao de 8 horas."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.auth_secret_key, algorithm=ALGORITHM)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    """Dependency: valida o token JWT e retorna o usuario autenticado.

    Se AUTH_SECRET_KEY nao estiver configurado (modo dev), retorna usuario admin
    para permitir uso sem autenticacao.
    """
    if not settings.auth_secret_key:
        # Modo dev — sem autenticacao
        return {"username": "dev", "name": "Dev User", "email": "", "roles": ["admin"]}

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacao nao fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.auth_secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    users = _load_users()
    user_data = users.get(username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado.",
        )

    return {
        "username": username,
        "name": user_data.get("name", username),
        "email": user_data.get("email", ""),
        "roles": user_data.get("roles", []),
    }


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency: exige que o usuario autenticado tenha role 'admin'."""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user
