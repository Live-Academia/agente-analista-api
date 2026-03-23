"""Router: POST /auth/token e GET /auth/me — Autenticacao JWT."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.schemas import Token, UserInfo
from api.security import authenticate_user, create_access_token, get_current_user

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Autentica usuario e retorna JWT Bearer token (valido por 8 horas)."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["username"], "roles": user["roles"]})
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserInfo)
async def me(current_user: dict = Depends(get_current_user)) -> UserInfo:
    """Retorna informacoes do usuario autenticado."""
    return UserInfo(**current_user)
