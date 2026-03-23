"""Router: POST /api/analyze — Upload de arquivo ou config de fonte de dados."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from api.schemas import AnalysisResult
from api.security import get_current_user, require_admin
from deep_agent.graph import build_graph

router = APIRouter()


def _run_pipeline(file_path: str | None = None, data_source=None, source_name: str = "") -> AnalysisResult:
    """Executa o grafo LangGraph e retorna AnalysisResult JSON-serializavel."""
    graph = build_graph()
    result = graph.invoke({
        "file_path": file_path,
        "data_source": data_source,
        "mode": "report",
        "user_question": None,
        "insights": [],
        "patterns": [],
    })

    if result.get("error"):
        raise HTTPException(status_code=422, detail=result["error"])

    return AnalysisResult(
        data_summary=result.get("data_summary") or {},
        statistical_analysis=result.get("statistical_analysis") or {},
        patterns=result.get("patterns") or [],
        insights=result.get("insights") or [],
        source_name=source_name,
    )


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_file(
    file: UploadFile = File(...),
    _user: dict = Depends(get_current_user),
) -> AnalysisResult:
    """Recebe upload de arquivo CSV/Excel e retorna analise completa."""
    suffix = Path(file.filename or "data.csv").suffix.lower()
    if suffix not in (".csv", ".xlsx", ".xls"):
        raise HTTPException(status_code=400, detail="Formato nao suportado. Use .csv, .xlsx ou .xls")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        return _run_pipeline(file_path=tmp_path, source_name=file.filename or "arquivo")
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except OSError:
            pass


@router.post("/analyze/google-sheets", response_model=AnalysisResult)
async def analyze_google_sheets(
    sheet_id: str = Form(...),
    tab_name: str = Form(""),
    _user: dict = Depends(require_admin),
) -> AnalysisResult:
    """Conecta a uma planilha Google Sheets e retorna analise. Somente admin."""
    from deep_agent.config import settings
    from deep_agent.sources.google_sheets import GoogleSheetsSource

    if not settings.google_credentials_json:
        raise HTTPException(status_code=400, detail="GOOGLE_CREDENTIALS_JSON nao configurado no servidor.")

    source = GoogleSheetsSource(sheet_id, settings.google_credentials_json, tab_name)
    return _run_pipeline(data_source=source, source_name=f"Google Sheets: {sheet_id}")


@router.post("/analyze/supabase", response_model=AnalysisResult)
async def analyze_supabase(
    table_name: str = Form(...),
    query: str = Form(""),
    _user: dict = Depends(require_admin),
) -> AnalysisResult:
    """Conecta a uma tabela Supabase e retorna analise. Somente admin."""
    from deep_agent.config import settings
    from deep_agent.sources.supabase_source import SupabaseSource

    if not settings.supabase_url:
        raise HTTPException(status_code=400, detail="SUPABASE_URL nao configurado no servidor.")

    source = SupabaseSource(table_name, settings.supabase_url, settings.supabase_key, query)
    return _run_pipeline(data_source=source, source_name=f"Supabase: {table_name}")


@router.post("/analyze/bigquery", response_model=AnalysisResult)
async def analyze_bigquery(
    table_id: str = Form(""),
    sql_query: str = Form(""),
    _user: dict = Depends(require_admin),
) -> AnalysisResult:
    """Conecta ao BigQuery e retorna analise. Somente admin."""
    from deep_agent.config import settings
    from deep_agent.sources.bigquery import BigQuerySource

    if not settings.gcp_project_id:
        raise HTTPException(status_code=400, detail="GCP_PROJECT_ID nao configurado no servidor.")
    if not table_id and not sql_query:
        raise HTTPException(status_code=400, detail="Informe table_id ou sql_query.")

    source = BigQuerySource(settings.gcp_project_id, table_id, sql_query)
    return _run_pipeline(data_source=source, source_name="BigQuery")
