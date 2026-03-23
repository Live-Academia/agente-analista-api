"""Template de analise: Financeiro."""
from deep_agent.templates.base import AnalysisTemplate

FINANCIAL = AnalysisTemplate(
    name="financeiro",
    label="Financeiro",
    description="Analise de fluxo de caixa, despesas, receitas e rentabilidade.",
    key_columns=[
        "despesa", "receita", "lucro", "custo", "orcamento",
        "pagamento", "conta", "saldo", "fluxo", "categoria",
        "debito", "credito", "margem", "resultado",
    ],
    kpis=[
        "Receita Total",
        "Despesa Total",
        "Lucro / Margem",
        "Fluxo de Caixa",
        "Maiores Categorias de Custo",
    ],
    insight_focus=(
        "Foque em: (1) composicao e evolucao das despesas por categoria, "
        "(2) margem liquida e bruta ao longo do tempo, "
        "(3) categorias com maior crescimento de custo (alertas), "
        "(4) aderencia ao orcamento (realizado vs planejado se disponivel), "
        "(5) oportunidades de reducao de custo ou melhora de margem."
    ),
    suggested_questions=[
        "Quais sao as maiores categorias de despesa?",
        "Qual e a margem de lucro media?",
        "Como evoluiu o fluxo de caixa?",
        "Existem despesas anomalas ou outliers?",
        "Quais meses tiveram resultado negativo?",
        "Qual a proporcao despesa/receita?",
    ],
)
