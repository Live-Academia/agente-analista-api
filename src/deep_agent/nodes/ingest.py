from __future__ import annotations

from deep_agent.sources.base import FileDataSource
from deep_agent.state import AgentState
from deep_agent.utils.file_loader import build_data_summary


def ingest_node(state: AgentState) -> dict:
    """No de ingestao: carrega dados de qualquer fonte e gera resumo."""
    try:
        # Dispatch: DataSource customizado ou file_path (retrocompativel)
        data_source = state.get("data_source")
        if data_source is not None:
            df = data_source.fetch()
        elif state.get("file_path"):
            source = FileDataSource(state["file_path"])
            df = source.fetch()
        else:
            return {"error": "Nenhuma fonte de dados fornecida."}

        summary = build_data_summary(df)
        return {
            "raw_data": df,
            "data_summary": summary,
        }
    except Exception as e:
        return {"error": str(e)}
