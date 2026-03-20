from __future__ import annotations

import json

from deep_agent.config import get_llm
from deep_agent.prompts.qa_prompt import qa_prompt
from deep_agent.state import AgentState


def _format_qa_data(state: AgentState) -> dict:
    """Prepara os dados do state para o prompt de Q&A."""
    summary = state.get("data_summary") or {}
    stats = state.get("statistical_analysis") or {}
    shape = summary.get("shape", {})

    return {
        "rows": shape.get("rows", "N/A"),
        "columns": shape.get("columns", "N/A"),
        "numeric_columns": ", ".join(summary.get("numeric_columns", [])),
        "categorical_columns": ", ".join(summary.get("categorical_columns", [])),
        "describe": json.dumps(summary.get("describe", {}), indent=2, default=str),
        "numeric_profile": json.dumps(stats.get("numeric_profile", {}), indent=2, default=str),
        "correlations": json.dumps(stats.get("high_correlations", []), indent=2, default=str),
        "outliers": json.dumps(stats.get("outliers", {}), indent=2, default=str),
        "temporal": json.dumps(stats.get("temporal", {}), indent=2, default=str) or "Nenhuma coluna de data detectada",
        "segments": json.dumps(stats.get("segments", {}), indent=2, default=str) or "Sem segmentacao disponivel",
        "business_metrics": json.dumps(stats.get("business_metrics", {}), indent=2, default=str) or "Sem metricas de negocio",
        "patterns": "\n".join(f"- {p}" for p in state.get("patterns", [])) or "Nenhum padrao detectado",
        "head": json.dumps(summary.get("head", []), indent=2, default=str),
        "question": state.get("user_question", ""),
    }


def qa_node(state: AgentState) -> dict:
    """No de Q&A: responde uma pergunta especifica sobre os dados."""
    if state.get("error"):
        return {}

    try:
        llm = get_llm()

        prompt_data = _format_qa_data(state)
        chain = qa_prompt | llm
        response = chain.invoke(prompt_data)

        return {"qa_answer": response.content}
    except Exception as e:
        return {"qa_answer": f"Erro ao consultar o LLM: {e}"}
