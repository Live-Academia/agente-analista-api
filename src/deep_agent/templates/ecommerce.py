"""Template de analise: E-commerce."""
from deep_agent.templates.base import AnalysisTemplate

ECOMMERCE = AnalysisTemplate(
    name="ecommerce",
    label="E-commerce",
    description="Analise de loja online: conversao, produtos, carrinho e entregas.",
    key_columns=[
        "sku", "carrinho", "checkout", "entrega", "frete",
        "ticket", "conversao", "sessao", "abandono", "categoria",
        "estoque", "devolucao", "avaliacao", "canal",
    ],
    kpis=[
        "Taxa de Conversao",
        "Ticket Medio",
        "Taxa de Abandono de Carrinho",
        "Produtos Mais Vendidos",
        "Custo de Frete Medio",
    ],
    insight_focus=(
        "Foque em: (1) funil de conversao e pontos de abandono, "
        "(2) categorias e SKUs com melhor e pior desempenho, "
        "(3) impacto do frete na taxa de conversao, "
        "(4) canais de aquisicao mais eficientes (se disponivel), "
        "(5) padroes de devolucao e impacto na margem, "
        "(6) sazonalidade e picos de demanda."
    ),
    suggested_questions=[
        "Qual e a taxa de conversao geral?",
        "Quais produtos tem maior taxa de abandono?",
        "Como o frete afeta as vendas?",
        "Quais categorias tem melhor desempenho?",
        "Qual e a taxa de devolucao?",
        "Quais canais trazem mais receita?",
    ],
)
