"""Auto-deteccao de template baseada nos nomes de colunas do dataset."""
from __future__ import annotations

from deep_agent.templates import TEMPLATES


def detect_template(columns: list[str]) -> str | None:
    """Retorna o nome do template mais adequado, ou None se nao detectar.

    Exige pelo menos 2 palavras-chave presentes nos nomes de colunas
    para evitar falsos positivos.
    """
    cols_lower = [c.lower() for c in columns]
    best: str | None = None
    best_score = 0

    for tmpl in TEMPLATES.values():
        score = sum(
            1
            for kw in tmpl.key_columns
            if any(kw in col for col in cols_lower)
        )
        if score > best_score:
            best_score = score
            best = tmpl.name

    return best if best_score >= 2 else None
