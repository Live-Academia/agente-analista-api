from __future__ import annotations

import json

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from deep_agent.sources.base import DataSource

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSheetsSource(DataSource):
    """Fonte de dados a partir de Google Sheets via Service Account."""

    def __init__(self, sheet_id: str, credentials_json: str, tab_name: str = ""):
        self.sheet_id = sheet_id
        self.credentials_json = credentials_json
        self.tab_name = tab_name

    def _get_client(self) -> gspread.Client:
        creds_data = json.loads(self.credentials_json)
        credentials = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
        return gspread.authorize(credentials)

    def fetch(self) -> pd.DataFrame:
        gc = self._get_client()
        spreadsheet = gc.open_by_key(self.sheet_id)

        if self.tab_name:
            worksheet = spreadsheet.worksheet(self.tab_name)
        else:
            worksheet = spreadsheet.sheet1

        records = worksheet.get_all_records()
        if not records:
            raise ValueError(f"Planilha '{self.sheet_id}' esta vazia ou sem dados.")

        return pd.DataFrame(records)

    def get_name(self) -> str:
        tab = f" ({self.tab_name})" if self.tab_name else ""
        return f"Google Sheets: {self.sheet_id}{tab}"
