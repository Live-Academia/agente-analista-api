from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_file(file_path: str) -> pd.DataFrame:
    """Carrega um arquivo CSV ou Excel em um DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Formato não suportado: {suffix}. Use .csv, .xlsx ou .xls")


def build_data_summary(df: pd.DataFrame) -> dict:
    """Constrói um resumo compacto do DataFrame para enviar ao LLM."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Amostra representativa: head + tail + amostra aleatória
    sample_size = min(10, len(df))
    if len(df) > 10:
        sample = pd.concat([
            df.head(3),
            df.sample(min(4, len(df) - 6), random_state=42),
            df.tail(3),
        ]).drop_duplicates()
    else:
        sample = df

    summary = {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "null_counts": df.isnull().sum().to_dict(),
        "null_pct": {col: round(df[col].isnull().sum() / len(df) * 100, 1) for col in df.columns if df[col].isnull().sum() > 0},
        "head": sample.to_dict(orient="records"),
        "describe": df.describe(include="all").fillna("N/A").to_dict(),
        "unique_counts": {col: int(df[col].nunique()) for col in categorical_cols},
    }
    return summary
