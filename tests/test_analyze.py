from deep_agent.nodes.analyze import analyze_node
from deep_agent.nodes.ingest import ingest_node


def test_analyze_node(sample_csv_path):
    # Primeiro ingere os dados
    state = {
        "file_path": sample_csv_path,
        "user_question": None,
        "mode": "report",
        "insights": [],
        "patterns": [],
    }
    state.update(ingest_node(state))

    # Depois analisa
    result = analyze_node(state)

    assert "statistical_analysis" in result
    assert "patterns" in result
    assert isinstance(result["statistical_analysis"]["high_correlations"], list)
    assert isinstance(result["statistical_analysis"]["outliers"], dict)
    assert isinstance(result["statistical_analysis"]["distributions"], dict)


def test_analyze_detects_correlations(sample_csv_path):
    state = {
        "file_path": sample_csv_path,
        "user_question": None,
        "mode": "report",
        "insights": [],
        "patterns": [],
    }
    state.update(ingest_node(state))
    result = analyze_node(state)

    # vendas, custo e lucro devem ter alta correlação
    correlations = result["statistical_analysis"]["high_correlations"]
    col_pairs = {(c["col1"], c["col2"]) for c in correlations}
    assert len(correlations) > 0, "Deveria detectar correlações entre vendas/custo/lucro"
