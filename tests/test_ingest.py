from deep_agent.nodes.ingest import ingest_node
from deep_agent.utils.file_loader import build_data_summary, load_file


def test_load_csv(sample_csv_path):
    df = load_file(sample_csv_path)
    assert df.shape[0] == 20
    assert "vendas" in df.columns


def test_build_data_summary(sample_csv_path):
    df = load_file(sample_csv_path)
    summary = build_data_summary(df)
    assert summary["shape"]["rows"] == 20
    assert "vendas" in summary["columns"]
    assert len(summary["head"]) >= 5


def test_ingest_node(sample_csv_path):
    state = {
        "file_path": sample_csv_path,
        "user_question": None,
        "mode": "report",
        "insights": [],
        "patterns": [],
    }
    result = ingest_node(state)
    assert result["raw_data"] is not None
    assert result["data_summary"]["shape"]["rows"] == 20


def test_ingest_node_file_not_found():
    state = {
        "file_path": "nao_existe.csv",
        "user_question": None,
        "mode": "report",
        "insights": [],
        "patterns": [],
    }
    result = ingest_node(state)
    assert "error" in result
