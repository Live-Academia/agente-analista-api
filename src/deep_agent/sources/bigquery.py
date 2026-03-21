from __future__ import annotations

import pandas as pd
from google.cloud import bigquery

from deep_agent.sources.base import DataSource


class BigQuerySource(DataSource):
    """Fonte de dados a partir de tabela ou query no BigQuery."""

    def __init__(self, project_id: str, table_id: str = "", sql_query: str = ""):
        self.project_id = project_id
        self.table_id = table_id
        self.sql_query = sql_query

        if not table_id and not sql_query:
            raise ValueError("Informe table_id ou sql_query.")

    MAX_ROWS = 10_000

    def fetch(self) -> pd.DataFrame:
        client = bigquery.Client(project=self.project_id)

        if self.sql_query:
            normalized = self.sql_query.strip()
            if not normalized.upper().startswith("SELECT"):
                raise ValueError("Apenas queries SELECT sao permitidas no BigQuery.")
            safe_query = f"SELECT * FROM ({normalized}) LIMIT {self.MAX_ROWS}"
            query_job = client.query(safe_query)
            df = query_job.to_dataframe()
        else:
            table = client.get_table(self.table_id)
            df = client.list_rows(table, max_results=self.MAX_ROWS).to_dataframe()

        if df.empty:
            raise ValueError(f"Consulta retornou vazia: {self.table_id or self.sql_query[:50]}")

        return df

    def get_name(self) -> str:
        if self.sql_query:
            return f"BigQuery: SQL Query"
        return f"BigQuery: {self.table_id}"
