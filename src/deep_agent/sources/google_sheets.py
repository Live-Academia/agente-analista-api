from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from typing import Optional

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from deep_agent.sources.base import DataSource

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


@lru_cache(maxsize=4)
def _get_service_account_client(credentials_hash: str, credentials_json: str) -> gspread.Client:
    """Singleton por conjunto de credenciais — recriado apenas se as credenciais mudarem."""
    creds_data = json.loads(credentials_json)
    credentials = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
    return gspread.authorize(credentials)


def _get_oauth2_client(authorized_user_json: str) -> gspread.Client:
    """Cria cliente gspread usando OAuth2 com refresh automatico de token.

    Usa os scopes originais do token (nao sobrescreve) para evitar
    invalid_scope ao renovar credenciais geradas via gcloud ADC.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials as OAuth2Credentials

    auth_data = json.loads(authorized_user_json)
    # Nao passar scopes — usa os scopes originais do token (ex: cloud-platform)
    # que ja incluem acesso a Sheets e Drive
    credentials = OAuth2Credentials(
        token=auth_data.get("access_token"),
        refresh_token=auth_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=auth_data.get("client_id"),
        client_secret=auth_data.get("client_secret"),
    )
    # Forcar refresh para garantir token valido
    credentials.refresh(Request())
    return gspread.authorize(credentials)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type(gspread.exceptions.APIError),
    reraise=True,
)
def _fetch_with_retry(worksheet: gspread.Worksheet) -> list[dict]:
    """Busca registros com retry automatico em erros transientes da Google API."""
    return worksheet.get_all_records()


class GoogleSheetsSource(DataSource):
    """Fonte de dados a partir de Google Sheets via Service Account ou OAuth2.

    O cliente gspread e mantido como singleton (por conjunto de credenciais)
    para evitar reconexoes desnecessarias. Erros transientes (429, 503) sao
    retentados automaticamente com exponential backoff via tenacity.
    """

    _singleton_client: Optional[gspread.Client] = None

    def __init__(
        self,
        sheet_id: str,
        credentials_json: str,
        tab_name: str = "",
        auth_method: str = "service_account",
        authorized_user_json: str = "",
    ):
        self.sheet_id = sheet_id
        self.credentials_json = credentials_json
        self.tab_name = tab_name
        self.auth_method = auth_method
        self.authorized_user_json = authorized_user_json

    @classmethod
    def init_client(
        cls,
        credentials_json: str,
        auth_method: str = "service_account",
        authorized_user_json: str = "",
    ) -> None:
        """Inicializa o singleton na startup do servidor (FastAPI lifespan).

        Chame este metodo uma vez na inicializacao para que todas as instancias
        de GoogleSheetsSource reusem a mesma conexao autenticada.
        """
        if auth_method == "oauth2" and authorized_user_json:
            cls._singleton_client = _get_oauth2_client(authorized_user_json)
        else:
            creds_hash = hashlib.sha256(credentials_json.encode()).hexdigest()
            cls._singleton_client = _get_service_account_client(creds_hash, credentials_json)

    def _get_client(self) -> gspread.Client:
        """Retorna o singleton se inicializado, caso contrario cria com cache por credenciais."""
        if self.__class__._singleton_client is not None:
            return self.__class__._singleton_client

        if self.auth_method == "oauth2" and self.authorized_user_json:
            return _get_oauth2_client(self.authorized_user_json)

        creds_hash = hashlib.sha256(self.credentials_json.encode()).hexdigest()
        return _get_service_account_client(creds_hash, self.credentials_json)

    def fetch(self) -> pd.DataFrame:
        try:
            gc = self._get_client()
            spreadsheet = gc.open_by_key(self.sheet_id)
        except gspread.exceptions.NoValidUrlKeyFound:
            raise ValueError(
                f"Sheet ID invalido: '{self.sheet_id}'. Verifique o ID ou URL da planilha."
            )
        except gspread.exceptions.SpreadsheetNotFound:
            raise ValueError(
                f"Planilha nao encontrada: '{self.sheet_id}'. "
                "Verifique se o service account tem acesso (compartilhe a planilha com o email do service account)."
            )
        except gspread.exceptions.APIError as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status == 403:
                raise ValueError(
                    f"Sem permissao para acessar '{self.sheet_id}'. "
                    "Compartilhe a planilha com o email do service account."
                )
            if status == 429:
                raise ValueError(
                    "Limite de requisicoes da Google API atingido. Aguarde alguns minutos e tente novamente."
                )
            raise

        try:
            worksheet = (
                spreadsheet.worksheet(self.tab_name) if self.tab_name else spreadsheet.sheet1
            )
        except gspread.exceptions.WorksheetNotFound:
            available = [ws.title for ws in spreadsheet.worksheets()]
            raise ValueError(
                f"Aba '{self.tab_name}' nao encontrada. "
                f"Abas disponiveis: {available}"
            )

        records = _fetch_with_retry(worksheet)
        if not records:
            raise ValueError(
                f"Planilha '{self.sheet_id}' esta vazia ou sem dados na aba selecionada."
            )

        return pd.DataFrame(records)

    def get_name(self) -> str:
        tab = f" ({self.tab_name})" if self.tab_name else ""
        return f"Google Sheets: {self.sheet_id}{tab}"
