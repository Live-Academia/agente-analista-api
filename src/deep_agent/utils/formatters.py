from __future__ import annotations

from datetime import datetime


def dict_to_markdown_table(data: dict, headers: tuple[str, str] = ("Metrica", "Valor")) -> str:
    """Converte um dicionario simples em tabela Markdown."""
    lines = [f"| {headers[0]} | {headers[1]} |", "| --- | --- |"]
    for key, value in data.items():
        if isinstance(value, dict):
            value = ", ".join(f"{k}: {v}" for k, v in value.items())
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def format_report(
    data_summary: dict,
    statistical_analysis: dict,
    patterns: list[str],
    insights: list[str],
) -> str:
    """Compoe o relatorio final em Markdown."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    shape = data_summary.get("shape", {})

    sections = [
        f"# Relatorio de Analise de Dados",
        f"**Gerado em:** {now}\n",
        "---\n",
        "## 1. Visao Geral dos Dados\n",
        f"- **Linhas:** {shape.get('rows', 'N/A')}",
        f"- **Colunas:** {shape.get('columns', 'N/A')}",
        f"- **Colunas numericas:** {', '.join(data_summary.get('numeric_columns', []))}",
        f"- **Colunas categoricas:** {', '.join(data_summary.get('categorical_columns', []))}\n",
    ]

    # Valores nulos
    null_counts = data_summary.get("null_counts", {})
    non_zero_nulls = {k: v for k, v in null_counts.items() if v > 0}
    if non_zero_nulls:
        sections.append("### Valores Nulos\n")
        sections.append(dict_to_markdown_table(non_zero_nulls, ("Coluna", "Nulos")))
        sections.append("")

    # Metricas de negocio
    business = statistical_analysis.get("business_metrics", {})
    if business:
        sections.append("---\n")
        sections.append("## 2. Metricas de Negocio\n")
        labels = {
            "total_vendas": "Total Vendas",
            "total_lucro": "Total Lucro",
            "total_custo": "Total Custo",
            "margem_lucro_pct": "Margem de Lucro (%)",
            "ticket_medio": "Ticket Medio",
            "pareto_top20_pct": "Top 20% concentram (%)",
            "custo_sobre_receita_pct": "Custo/Receita (%)",
        }
        formatted = {labels.get(k, k): f"{v:,.2f}" if isinstance(v, float) else v for k, v in business.items()}
        sections.append(dict_to_markdown_table(formatted))
        sections.append("")

    # Analise estatistica
    sections.append("---\n")
    sections.append("## 3. Analise Estatistica\n")

    if correlations := statistical_analysis.get("high_correlations"):
        sections.append("### Correlacoes Relevantes\n")
        for corr in correlations:
            sections.append(f"- **{corr['col1']}** <-> **{corr['col2']}**: {corr['value']:.3f}")
        sections.append("")

    if outlier_info := statistical_analysis.get("outliers"):
        sections.append("### Outliers Detectados (IQR)\n")
        for col, info in outlier_info.items():
            if isinstance(info, dict):
                sections.append(f"- **{col}**: {info['count']} outliers (limites: {info['lower_bound']} a {info['upper_bound']})")
            else:
                sections.append(f"- **{col}**: {info} outliers")
        sections.append("")

    if distributions := statistical_analysis.get("distributions"):
        sections.append("### Distribuicoes Categoricas (Top 5)\n")
        for col, dist in distributions.items():
            sections.append(f"**{col}:**")
            for val, count in list(dist.items())[:5]:
                sections.append(f"  - {val}: {count}")
            sections.append("")

    # Analise temporal
    temporal = statistical_analysis.get("temporal", {})
    if temporal:
        sections.append("---\n")
        sections.append("## 4. Analise Temporal\n")
        sections.append(f"- **Periodo:** {temporal.get('date_range', 'N/A')}")
        sections.append(f"- **Periodos analisados:** {temporal.get('period_count', 'N/A')}\n")
        if growth := temporal.get("growth"):
            sections.append("### Tendencias de Crescimento\n")
            for col, g in growth.items():
                sections.append(f"- **{col}**: {g['trend']} (media: {g['avg_growth_pct']:+.1f}%)")
            sections.append("")

    # Padroes
    if patterns:
        sections.append("---\n")
        sections.append("## 5. Padroes Detectados\n")
        for p in patterns:
            sections.append(f"- {p}")
        sections.append("")

    # Insights do LLM
    if insights:
        sections.append("---\n")
        sections.append("## 6. Insights (IA)\n")
        for i, insight in enumerate(insights, 1):
            sections.append(f"**{i}.** {insight}\n")

    sections.append("---\n")
    sections.append("*Relatorio gerado automaticamente pelo Deep Agent.*")

    return "\n".join(sections)
