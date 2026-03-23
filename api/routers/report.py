"""Router: POST /api/report — Gera relatorio Markdown com insights de IA."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from api.schemas import ReportRequest, ReportResponse
from api.security import get_current_user
from deep_agent.export.pdf_exporter import markdown_to_pdf
from deep_agent.nodes.insights import insights_node
from deep_agent.nodes.report import report_node
from deep_agent.storage.logger import log_operation

router = APIRouter()


def _build_state(req: ReportRequest) -> dict:
    a = req.analysis_state
    return {
        "data_summary": a.get("data_summary", {}),
        "statistical_analysis": a.get("statistical_analysis", {}),
        "patterns": a.get("patterns", []),
        "insights": a.get("insights", []),
        "mode": "report",
        "raw_data": None,
        "file_path": None,
        "data_source": None,
        "user_question": None,
        "template": None,
        "error": None,
        "report": None,
        "qa_answer": None,
    }


@router.post("/report", response_model=ReportResponse)
async def generate_report(
    req: ReportRequest,
    _user: dict = Depends(get_current_user),
) -> ReportResponse:
    """Gera relatorio Markdown completo a partir do analysis_state."""
    state = _build_state(req)
    source_name = state["data_summary"].get("source_name", "")

    # Gera insights via LLM (se nao houver ainda)
    if not state["insights"]:
        insights_result = insights_node(state)
        if insights_result.get("error"):
            log_operation("report", status="error", username=_user.get("username"),
                          source_name=source_name, metadata={"error": insights_result["error"]})
            raise HTTPException(status_code=500, detail=insights_result["error"])
        if "insights" not in insights_result:
            raise HTTPException(status_code=500, detail="Falha ao gerar insights — resposta vazia do LLM.")
        state["insights"] = insights_result["insights"]

    # Gera relatorio Markdown
    report_result = report_node(state)
    report_text = report_result.get("report", "")
    if not report_text:
        raise HTTPException(status_code=500, detail="Falha ao gerar relatorio.")

    log_operation("report", status="ok", username=_user.get("username"),
                  source_name=source_name,
                  metadata={"session_id": req.analysis_state.get("session_id")})

    return ReportResponse(report_text=report_text)


@router.post("/report/pdf")
async def generate_report_pdf(
    req: ReportRequest,
    _user: dict = Depends(get_current_user),
) -> Response:
    """Gera PDF do relatorio e retorna como download direto."""
    report_resp = await generate_report(req, _user)
    source_name = req.analysis_state.get("data_summary", {}).get("source_name", "relatorio")
    pdf_bytes = markdown_to_pdf(report_resp.report_text, title=f"Relatorio — {source_name}")

    log_operation("report_pdf", status="ok", username=_user.get("username"),
                  source_name=source_name)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="relatorio.pdf"'},
    )
