import pandas as pd
import pytest

from deep_agent.sources.base import DataSource, FileDataSource


def test_file_data_source(sample_csv_path):
    source = FileDataSource(sample_csv_path)
    df = source.fetch()
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 20
    assert "vendas" in df.columns


def test_file_data_source_name(sample_csv_path):
    source = FileDataSource(sample_csv_path)
    assert "Arquivo:" in source.get_name()


def test_file_data_source_not_found():
    source = FileDataSource("nao_existe.csv")
    with pytest.raises(FileNotFoundError):
        source.fetch()


def test_datasource_is_abstract():
    with pytest.raises(TypeError):
        DataSource()


def test_ingest_node_with_data_source(sample_csv_path):
    """Testa ingest_node com DataSource em vez de file_path."""
    from deep_agent.nodes.ingest import ingest_node

    source = FileDataSource(sample_csv_path)
    state = {
        "file_path": None,
        "data_source": source,
        "user_question": None,
        "mode": "report",
        "insights": [],
        "patterns": [],
    }
    result = ingest_node(state)
    assert result["raw_data"] is not None
    assert result["data_summary"]["shape"]["rows"] == 20


def test_ingest_node_no_source():
    """Testa ingest_node sem nenhuma fonte."""
    from deep_agent.nodes.ingest import ingest_node

    state = {
        "file_path": None,
        "data_source": None,
        "user_question": None,
        "mode": "report",
        "insights": [],
        "patterns": [],
    }
    result = ingest_node(state)
    assert "error" in result
