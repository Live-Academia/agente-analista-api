from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from deep_agent.chains.qa import qa_node
from deep_agent.nodes.analyze import analyze_node
from deep_agent.nodes.ingest import ingest_node
from deep_agent.nodes.insights import insights_node
from deep_agent.nodes.report import report_node
from deep_agent.state import AgentState


def _route_after_analysis(state: AgentState) -> str:
    """Decide a rota após a análise: relatório completo ou Q&A."""
    if state.get("error"):
        return "end"
    if state.get("mode") == "qa" and state.get("user_question"):
        return "qa"
    return "report"


def build_graph():
    """Constrói e compila o StateGraph do Deep Agent."""
    graph = StateGraph(AgentState)

    # Adicionar nós
    graph.add_node("ingest", ingest_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("insights", insights_node)
    graph.add_node("report", report_node)
    graph.add_node("qa", qa_node)

    # Edges lineares
    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "analyze")

    # Edge condicional após análise
    graph.add_conditional_edges(
        "analyze",
        _route_after_analysis,
        {
            "report": "insights",
            "qa": "qa",
            "end": END,
        },
    )

    # Edges terminais
    graph.add_edge("insights", "report")
    graph.add_edge("report", END)
    graph.add_edge("qa", END)

    return graph.compile()
