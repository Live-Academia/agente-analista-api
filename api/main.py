"""FastAPI app principal — Deep Agent API."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import analyze, chat, report

app = FastAPI(
    title="Deep Agent API",
    description="API REST para analise de dados inteligente com LangGraph + Claude/GPT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
