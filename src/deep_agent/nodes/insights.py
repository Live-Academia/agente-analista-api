from __future__ import annotations

import json
import re

from deep_agent.config import get_llm
from deep_agent.prompts.insight_prompt import insight_prompt
from deep_agent.state import AgentState


def _format_prompt_data(state: AgentState) -> dict:
    """Prepara os dados do state para injetar no prompt."""
    summary = state.get("data_summary") or {}
    stats = state.get("statistical_analysis") or {}
    shape = summary.get("shape", {})

    # Template focus: instrucao adicional se um template estiver ativo
    template_focus = "Nenhum template especifico — analise generica."
    template_name = state.get("template")
    if template_name:
        try:
            from deep_agent.templates import TEMPLATES
            tmpl = TEMPLATES.get(template_name)
            if tmpl:
                template_focus = f"Template '{tmpl.label}': {tmpl.insight_focus}"
        except Exception:
            pass

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
        "template_focus": template_focus,
    }


def _parse_insights(text: str) -> list[str]:
    """Extrai insights numerados da resposta do LLM."""
    lines = text.strip().split("\n")
    insights = []
    for line in lines:
        line = line.strip()
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", line)
        if cleaned and len(cleaned) > 10:
            insights.append(cleaned)
    return insights


def insights_node(state: AgentState) -> dict:
    """No de geracao de insights: envia dados ao LLM e extrai insights."""
    if state.get("error"):
        return {}

    try:
        llm = get_llm()

        prompt_data = _format_prompt_data(state)
        chain = insight_prompt | llm
        response = chain.invoke(prompt_data)

        insights = _parse_insights(response.content)
        return {"insights": insights}
    except Exception as e:
        return {"error": f"Falha ao gerar insights: {e}"}
