"""FastAPI app principal — Deep Agent API."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import analyze, chat, report, auth as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa recursos compartilhados na startup do servidor."""
    from deep_agent.config import settings

    if settings.google_credentials_json:
        from deep_agent.sources.google_sheets import GoogleSheetsSource

        GoogleSheetsSource.init_client(
            settings.google_credentials_json,
            auth_method=settings.google_auth_method,
            authorized_user_json=settings.google_authorized_user_json,
        )

    yield


app = FastAPI(
    title="Deep Agent API",
    description="API REST para analise de dados inteligente com LangGraph + Claude/GPT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — permite requisicoes do frontend (Vercel) e localhost
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,https://*.vercel.app",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(report.router, prefix="/api", tags=["report"])


@app.get("/health", tags=["health"])
async def health() -> dict:
    """Healthcheck endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", tags=["health"])
async def root() -> dict:
    """Root redirect para docs."""
    return {"message": "Deep Agent API — acesse /docs para a documentacao"}
