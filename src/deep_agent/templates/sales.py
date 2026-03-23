"""Template de analise: Vendas."""
from deep_agent.templates.base import AnalysisTemplate

SALES = AnalysisTemplate(
    name="vendas",
    label="Vendas",
    description="Analise de desempenho comercial: receita, produtos, clientes e tendencias.",
    key_columns=[
        "venda", "receita", "produto", "cliente", "pedido",
        "valor", "quantidade", "ticket", "faturamento", "item",
    ],
    kpis=[
        "Receita Total",
        "Ticket Medio",
        "Total de Pedidos",
        "Produtos Mais Vendidos",
        "Clientes Mais Ativos",
    ],
    insight_focus=(
        "Foque em: (1) produtos/servicos com maior receita e margem, "
        "(2) sazonalidade e tendencias temporais de vendas, "
        "(3) perfil dos clientes mais rentaveis (Pareto 80/20), "
        "(4) produtos com queda de demanda ou oportunidades de upsell, "
        "(5) comparacao de periodos (MoM, YoY se disponivel)."
    ),
    suggested_questions=[
        "Quais sao os 5 produtos mais vendidos?",
        "Como evoluiu a receita ao longo do tempo?",
        "Qual e o ticket medio por cliente?",
        "Existe sazonalidade nas vendas?",
        "Quais clientes representam 80% da receita?",
        "Qual produto teve maior crescimento recente?",
    ],
)
