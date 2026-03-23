"""Pydantic schemas para a API REST do Deep Agent."""

from __future__ import annotations

from pydantic import BaseModel


class AnalysisResult(BaseModel):
    """Resultado da analise retornado pelo endpoint /api/analyze."""

    data_summary: dict
    statistical_analysis: dict
    patterns: list[str]
    insights: list[str]
    source_name: str
    error: str | None = None


class ChatRequest(BaseModel):
    """Corpo da requisicao para /api/chat e /api/chat/stream."""

    question: str
    analysis_state: dict  # AnalysisResult serializado


class ChatResponse(BaseModel):
    """Resposta do endpoint /api/chat."""

    answer: str


class ReportRequest(BaseModel):
    """Corpo da requisicao para /api/report."""

    analysis_state: dict  # AnalysisResult serializado


class ReportResponse(BaseModel):
    """Resposta do endpoint /api/report."""

    report_text: str


# ── Auth ────────────────────────────────────────────────────────────────────


class Token(BaseModel):
    """JWT Bearer token retornado pelo endpoint /auth/token."""

    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """Informacoes do usuario autenticado retornadas pelo endpoint /auth/me."""

    username: str
    name: str
    email: str
    roles: list[str]
