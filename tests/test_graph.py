from deep_agent.graph import build_graph


def test_graph_compiles():
    """Testa que o grafo compila sem erros."""
    graph = build_graph()
    assert graph is not None
