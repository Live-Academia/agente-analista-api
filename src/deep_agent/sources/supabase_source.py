from __future__ import annotations

import pandas as pd

try:
    from supabase import create_client
except ImportError:
    create_client = None

from deep_agent.sources.base import DataSource


class SupabaseSource(DataSource):
    """Fonte de dados a partir de tabela no Supabase."""

    def __init__(self, table_name: str, url: str, key: str, query: str = ""):
        self.table_name = table_name
        self.url = url
        self.key = key
        self.query = query

    def fetch(self) -> pd.DataFrame:
        if create_client is None:
            raise ImportError("Instale o pacote 'supabase': pip install supabase")
        client = create_client(self.url, self.key)

        if self.query:
            response = client.table(self.table_name).select(self.query).limit(10000).execute()
        else:
            response = client.table(self.table_name).select("*").limit(10000).execute()

        if not response.data:
            raise ValueError(f"Tabela '{self.table_name}' esta vazia ou nao existe.")

        return pd.DataFrame(response.data)

    def get_name(self) -> str:
        return f"Supabase: {self.table_name}"
