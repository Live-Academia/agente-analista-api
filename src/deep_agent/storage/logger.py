"""Logger estruturado para o Deep Agent — salva logs no Supabase."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator

from deep_agent.config import settings


def _get_client():
    if not settings.supabase_url or not settings.supabase_key:
        return None
    try:
        from supabase import create_client
        return create_client(settings.supabase_url, settings.supabase_key)
    except Exception:
        return None


def log_operation(
    operation: str,
    status: str = "ok",
    session_id: str | None = None,
    username: str | None = None,
    source_name: str | None = None,
    duration_ms: int | None = None,
    metadata: dict | None = None,
) -> None:
    """Salva um log de operacao no Supabase.

    Silencia todos os erros para nunca interromper o fluxo principal.
    """
    client = _get_client()
    if not client:
        return
    try:
        client.table("_deepagent_logs").insert(
            {
                "session_id": session_id,
                "username": username,
                "operation": operation,
                "source_name": source_name,
                "duration_ms": duration_ms,
                "status": status,
                "metadata": metadata or {},
            }
        ).execute()
    except Exception:
        pass  # Nunca quebrar o fluxo principal por falha de log


@contextmanager
def timed_operation(
    operation: str,
    session_id: str | None = None,
    username: str | None = None,
    source_name: str | None = None,
    metadata: dict | None = None,
) -> Generator[None, None, None]:
    """Context manager que mede duracao e registra o log automaticamente.

    Exemplo::

        with timed_operation("analyze", username="admin", source_name="vendas.csv"):
            result = run_pipeline(...)
    """
    start = time.monotonic()
    try:
        yield
        duration = int((time.monotonic() - start) * 1000)
        log_operation(
            operation,
            status="ok",
            session_id=session_id,
            username=username,
            source_name=source_name,
            duration_ms=duration,
            metadata=metadata,
        )
    except Exception as exc:
        duration = int((time.monotonic() - start) * 1000)
        log_operation(
            operation,
            status="error",
            session_id=session_id,
            username=username,
            source_name=source_name,
            duration_ms=duration,
            metadata={"error": str(exc), **(metadata or {})},
        )
        raise
