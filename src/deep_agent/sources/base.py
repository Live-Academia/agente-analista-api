from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from deep_agent.utils.file_loader import load_file


class DataSource(ABC):
    """Classe base abstrata para todas as fontes de dados."""

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Busca os dados e retorna como DataFrame."""

    @abstractmethod
    def get_name(self) -> str:
        """Retorna nome descritivo da fonte."""


class FileDataSource(DataSource):
    """Fonte de dados a partir de arquivo local (CSV/Excel)."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def fetch(self) -> pd.DataFrame:
        return load_file(self.file_path)

    def get_name(self) -> str:
        return f"Arquivo: {self.file_path}"
