"""Historico persistente de analises e mensagens de chat no Supabase."""
from __future__ import annotations

from deep_agent.config import settings


def _get_client():
    if not settings.supabase_url or not settings.supabase_key:
        return None
    try:
        from supabase import create_client
        return create_client(settings.supabase_url, settings.supabase_key)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Analises
# ---------------------------------------------------------------------------

def save_analysis(
    session_id: str,
    username: str,
    source_name: str,
    data_summary: dict,
    statistical_analysis: dict | None,
    patterns: list,
    insights: list,
    template_used: str | None = None,
) -> None:
    """Salva (ou atualiza) uma analise completa no Supabase."""
    client = _get_client()
    if not client:
        return
    try:
        client.table("_deepagent_analyses").upsert(
            {
                "session_id": session_id,
                "username": username,
                "source_name": source_name,
                "template_used": template_used,
                "data_summary": data_summary,
                "statistical_analysis": statistical_analysis or {},
                "patterns": patterns,
                "insights": insights,
            }
        ).execute()
    except Exception:
        pass


def get_user_analyses(username: str, limit: int = 20) -> list[dict]:
    """Lista as analises mais recentes de um usuario (apenas metadados)."""
    client = _get_client()
    if not client:
        return []
    try:
        result = (
            client.table("_deepagent_analyses")
            .select("id,created_at,session_id,source_name,template_used")
            .eq("username", username)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def load_analysis(session_id: str) -> dict | None:
    """Carrega uma analise completa pelo session_id."""
    client = _get_client()
    if not client:
        return None
    try:
        result = (
            client.table("_deepagent_analyses")
            .select("*")
            .eq("session_id", session_id)
            .single()
            .execute()
        )
        return result.data
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Mensagens de chat
# ---------------------------------------------------------------------------

def save_message(session_id: str, username: str, role: str, content: str) -> None:
    """Salva uma mensagem de chat (role: 'user' ou 'assistant')."""
    client = _get_client()
    if not client:
        return
    try:
        client.table("_deepagent_messages").insert(
            {
                "session_id": session_id,
                "username": username,
                "role": role,
                "content": content,
            }
        ).execute()
    except Exception:
        pass


def get_session_messages(session_id: str) -> list[dict]:
    """Retorna todas as mensagens de uma sessao em ordem cronologica."""
    client = _get_client()
    if not client:
        return []
    try:
        result = (
            client.table("_deepagent_messages")
            .select("role,content,created_at")
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )
        return result.data or []
    except Exception:
        return []
