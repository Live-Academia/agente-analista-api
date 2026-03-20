from __future__ import annotations

from datetime import datetime
from pathlib import Path

from deep_agent.state import AgentState
from deep_agent.utils.formatters import format_report


def report_node(state: AgentState) -> dict:
    """Nó de relatório: compõe e salva o relatório Markdown."""
    if state.get("error"):
        return {}

    data_summary = state.get("data_summary") or {}
    statistical_analysis = state.get("statistical_analysis") or {}
    patterns = state.get("patterns", [])
    insights = state.get("insights", [])

    report_text = format_report(data_summary, statistical_analysis, patterns, insights)

    # Salvar no diretório output/ (ignorar falhas em ambientes read-only como Fly.io)
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"relatorio_{timestamp}.md"
        output_path.write_text(report_text, encoding="utf-8")
    except OSError:
        pass

    return {"report": report_text}
