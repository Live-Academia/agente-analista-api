"""Classe base para templates de analise predefinidos."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnalysisTemplate:
    """Define um modelo de analise para um dominio especifico.

    Attributes:
        name: Identificador interno (ex: "vendas").
        label: Nome exibido na UI (ex: "Vendas").
        description: Descricao curta para o usuario.
        key_columns: Palavras-chave esperadas nos nomes de colunas (para auto-deteccao).
        kpis: KPIs prioritarios que o dashboard deve destacar.
        insight_focus: Instrucao adicional ao LLM para direcionar os insights.
        suggested_questions: Perguntas pre-definidas no chat para o usuario clicar.
    """

    name: str
    label: str
    description: str
    key_columns: list[str] = field(default_factory=list)
    kpis: list[str] = field(default_factory=list)
    insight_focus: str = ""
    suggested_questions: list[str] = field(default_factory=list)
