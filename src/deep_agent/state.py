from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict):
    """Estado compartilhado entre todos os nós do grafo LangGraph."""

    # Inputs
    file_path: str | None
    data_source: Any | None  # DataSource (Any para evitar problemas de serializacao)
    user_question: str | None
    mode: str  # "report" ou "qa"

    # Data layer
    raw_data: Any  # pd.DataFrame (Any para evitar problemas de serialização)
    data_summary: dict | None

    # Analysis layer
    statistical_analysis: dict | None
    patterns: list[str]

    # LLM layer
    insights: list[str]
    qa_answer: str | None

    # Output layer
    report: str | None

    # Control
    error: str | None
