"""Router: POST /api/report — Gera relatorio Markdown com insights de IA."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.schemas import ReportRequest, ReportResponse
from api.security import get_current_user
from deep_agent.nodes.insights import insights_node
from deep_agent.nodes.report import report_node

router = APIRouter()


@router.post("/report", response_model=ReportResponse)
async def generate_report(
    req: ReportRequest,
    _user: dict = Depends(get_current_user),
) -> ReportResponse:
    """Gera relatorio Markdown completo a partir do analysis_state."""
    a = req.analysis_state
    state = {
        "data_summary": a.get("data_summary", {}),
        "statistical_analysis": a.get("statistical_analysis", {}),
        "patterns": a.get("patterns", []),
        "insights": a.get("insights", []),
        "mode": "report",
        "raw_data": None,
        "file_path": None,
        "data_source": None,
        "user_question": None,
        "error": None,
        "report": None,
        "qa_answer": None,
    }

    # Gera insights via LLM (se nao houver ainda)
    if not state["insights"]:
        insights_result = insights_node(state)
        if insights_result.get("error"):
            raise HTTPException(status_code=500, detail=insights_result["error"])
        if "insights" not in insights_result:
            raise HTTPException(status_code=500, detail="Falha ao gerar insights — resposta vazia do LLM.")
        state["insights"] = insights_result["insights"]

    # Gera relatorio Markdown
    report_result = report_node(state)
    report_text = report_result.get("report", "")
    if not report_text:
        raise HTTPException(status_code=500, detail="Falha ao gerar relatorio.")

    return ReportResponse(report_text=report_text)
