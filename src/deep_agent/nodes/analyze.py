from __future__ import annotations

import numpy as np
import pandas as pd

from deep_agent.state import AgentState


def _find_high_correlations(df: pd.DataFrame, threshold: float = 0.7) -> list[dict]:
    """Encontra pares de colunas numéricas com alta correlação."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return []

    corr_matrix = numeric_df.corr()
    pairs = []
    seen = set()

    for col1 in corr_matrix.columns:
        for col2 in corr_matrix.columns:
            if col1 == col2 or (col2, col1) in seen:
                continue
            value = corr_matrix.loc[col1, col2]
            if abs(value) >= threshold:
                pairs.append({"col1": col1, "col2": col2, "value": round(float(value), 4)})
                seen.add((col1, col2))

    return sorted(pairs, key=lambda x: abs(x["value"]), reverse=True)


def _detect_outliers_iqr(df: pd.DataFrame) -> dict:
    """Detecta outliers com detalhes: contagem, limites e valores extremos."""
    outliers = {}
    for col in df.select_dtypes(include="number").columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        count = int(mask.sum())
        if count > 0:
            outlier_vals = df.loc[mask, col]
            outliers[col] = {
                "count": count,
                "lower_bound": round(float(lower), 2),
                "upper_bound": round(float(upper), 2),
                "min_outlier": round(float(outlier_vals.min()), 2),
                "max_outlier": round(float(outlier_vals.max()), 2),
            }
    return outliers


def _get_distributions(df: pd.DataFrame) -> dict:
    """Obtém distribuições das colunas categóricas."""
    distributions = {}
    for col in df.select_dtypes(include=["object", "category"]).columns:
        distributions[col] = df[col].value_counts().head(10).to_dict()
    return distributions


def _compute_numeric_profile(df: pd.DataFrame) -> dict:
    """Perfil avançado das colunas numéricas: skewness, kurtosis, coef. variação."""
    profile = {}
    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if len(series) < 3:
            continue
        mean = series.mean()
        profile[col] = {
            "mean": round(float(mean), 2),
            "median": round(float(series.median()), 2),
            "std": round(float(series.std()), 2),
            "skewness": round(float(series.skew()), 3),
            "kurtosis": round(float(series.kurtosis()), 3),
            "cv": round(float(series.std() / mean * 100), 1) if mean != 0 else None,
        }
    return profile


def _detect_date_column(df: pd.DataFrame) -> str | None:
    """Detecta automaticamente a coluna de data."""
    for col in df.columns:
        if df[col].dtype == "datetime64[ns]":
            return col
        if df[col].dtype == "object":
            sample = df[col].dropna().head(20)
            try:
                pd.to_datetime(sample)
                return col
            except (ValueError, TypeError):
                continue
    return None


def _analyze_temporal(df: pd.DataFrame, date_col: str) -> dict:
    """Análise temporal: tendências, crescimento período a período."""
    df_temp = df.copy()
    df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors="coerce")
    df_temp = df_temp.dropna(subset=[date_col])

    if df_temp.empty:
        return {}

    df_temp["_period"] = df_temp[date_col].dt.to_period("M")
    numeric_cols = df_temp.select_dtypes(include="number").columns.tolist()

    if not numeric_cols:
        return {}

    # Agregação por período
    period_agg = df_temp.groupby("_period")[numeric_cols].sum()
    period_agg.index = period_agg.index.astype(str)

    # Crescimento período a período (%)
    growth = {}
    for col in numeric_cols:
        values = period_agg[col].values
        if len(values) >= 2:
            pct_changes = []
            for i in range(1, len(values)):
                if values[i - 1] != 0:
                    pct_changes.append(round(float((values[i] - values[i - 1]) / values[i - 1] * 100), 1))
            if pct_changes:
                growth[col] = {
                    "avg_growth_pct": round(float(np.mean(pct_changes)), 1),
                    "max_growth_pct": round(float(max(pct_changes)), 1),
                    "min_growth_pct": round(float(min(pct_changes)), 1),
                    "trend": "crescente" if np.mean(pct_changes) > 2 else "decrescente" if np.mean(pct_changes) < -2 else "estável",
                }

    return {
        "date_column": date_col,
        "period_count": len(period_agg),
        "date_range": f"{period_agg.index[0]} a {period_agg.index[-1]}",
        "period_totals": period_agg.to_dict(),
        "growth": growth,
    }


def _analyze_segments(df: pd.DataFrame) -> dict:
    """Segmentação: group-by nas colunas categóricas com métricas numéricas."""
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # Filtrar colunas de data detectadas
    categorical_cols = [c for c in categorical_cols if not _is_date_like(df[c])]

    if not categorical_cols or not numeric_cols:
        return {}

    segments = {}
    for cat_col in categorical_cols[:4]:  # Limitar a 4 colunas categóricas
        unique_count = df[cat_col].nunique()
        if unique_count < 2 or unique_count > 50:
            continue

        agg = df.groupby(cat_col)[numeric_cols].agg(["sum", "mean", "count"]).round(2)
        # Achatar MultiIndex
        agg.columns = [f"{col}_{stat}" for col, stat in agg.columns]
        segments[cat_col] = {
            "unique_values": unique_count,
            "aggregation": agg.to_dict(),
        }

    return segments


def _compute_business_metrics(df: pd.DataFrame) -> dict:
    """Calcula métricas de negócio quando colunas relevantes existem."""
    metrics = {}
    cols_lower = {c.lower(): c for c in df.columns}

    # Margem de lucro
    lucro_col = cols_lower.get("lucro") or cols_lower.get("profit")
    vendas_col = cols_lower.get("vendas") or cols_lower.get("revenue") or cols_lower.get("receita") or cols_lower.get("sales")

    if lucro_col and vendas_col:
        total_lucro = df[lucro_col].sum()
        total_vendas = df[vendas_col].sum()
        if total_vendas != 0:
            metrics["margem_lucro_pct"] = round(float(total_lucro / total_vendas * 100), 1)
        metrics["total_vendas"] = round(float(total_vendas), 2)
        metrics["total_lucro"] = round(float(total_lucro), 2)

    # Ticket médio
    unidades_col = cols_lower.get("unidades") or cols_lower.get("units") or cols_lower.get("quantidade") or cols_lower.get("qty")
    if vendas_col and unidades_col:
        total_unidades = df[unidades_col].sum()
        if total_unidades != 0:
            metrics["ticket_medio"] = round(float(df[vendas_col].sum() / total_unidades), 2)

    # Concentração (Pareto) — top 20% representam quanto %?
    if vendas_col:
        sorted_vals = df[vendas_col].sort_values(ascending=False).values
        n_top = max(1, int(len(sorted_vals) * 0.2))
        top_share = sorted_vals[:n_top].sum() / sorted_vals.sum() * 100
        metrics["pareto_top20_pct"] = round(float(top_share), 1)

    # Custo
    custo_col = cols_lower.get("custo") or cols_lower.get("cost")
    if custo_col:
        metrics["total_custo"] = round(float(df[custo_col].sum()), 2)
        if vendas_col:
            metrics["custo_sobre_receita_pct"] = round(float(df[custo_col].sum() / df[vendas_col].sum() * 100), 1)

    return metrics


def _is_date_like(series: pd.Series) -> bool:
    """Verifica se uma série parece ser data."""
    if series.dtype == "datetime64[ns]":
        return True
    if series.dtype == "object":
        try:
            pd.to_datetime(series.dropna().head(5))
            return True
        except (ValueError, TypeError):
            return False
    return False


def _detect_patterns(df: pd.DataFrame, correlations: list[dict], temporal: dict, segments: dict, business: dict) -> list[str]:
    """Detecta padrões nos dados combinando análise estatística, temporal e segmentada."""
    patterns = []
    total_rows = len(df)

    # Qualidade de dados: nulos
    for col in df.columns:
        null_pct = df[col].isnull().sum() / total_rows * 100
        if null_pct > 30:
            patterns.append(f"Coluna '{col}' possui {null_pct:.1f}% de valores nulos — possível problema de qualidade de dados")

    # Correlações fortes
    for corr in correlations[:3]:
        direction = "positiva" if corr["value"] > 0 else "negativa"
        patterns.append(f"Correlação {direction} forte entre '{corr['col1']}' e '{corr['col2']}' ({corr['value']:.3f})")

    # Variância zero
    for col in df.select_dtypes(include="number").columns:
        if df[col].std() == 0:
            patterns.append(f"Coluna '{col}' tem variância zero — considere removê-la da análise")

    # Tendências temporais
    if temporal and temporal.get("growth"):
        for col, g in temporal["growth"].items():
            if g["trend"] == "crescente":
                patterns.append(f"'{col}' apresenta tendência crescente ({g['avg_growth_pct']:+.1f}% médio por período)")
            elif g["trend"] == "decrescente":
                patterns.append(f"'{col}' apresenta tendência decrescente ({g['avg_growth_pct']:+.1f}% médio por período)")

    # Concentração Pareto
    if business.get("pareto_top20_pct"):
        pct = business["pareto_top20_pct"]
        if pct > 70:
            patterns.append(f"Alta concentração: top 20% das linhas representam {pct:.0f}% das vendas (efeito Pareto)")

    # Margem
    if business.get("margem_lucro_pct"):
        m = business["margem_lucro_pct"]
        if m < 20:
            patterns.append(f"Margem de lucro baixa: {m:.1f}% — investigar custos operacionais")
        elif m > 50:
            patterns.append(f"Margem de lucro alta: {m:.1f}% — posição competitiva forte")

    # Segmentos dominantes
    for cat_col, seg_data in segments.items():
        agg = seg_data.get("aggregation", {})
        # Procurar coluna de vendas na agregação
        sum_keys = [k for k in agg.keys() if k.endswith("_sum")]
        if sum_keys:
            first_sum = sum_keys[0]
            values = agg[first_sum]
            if values:
                top = max(values.items(), key=lambda x: x[1])
                total = sum(values.values())
                if total > 0:
                    share = top[1] / total * 100
                    if share > 40:
                        patterns.append(f"'{cat_col}' concentrada: '{top[0]}' representa {share:.0f}% do total de {first_sum.replace('_sum', '')}")

    return patterns


def analyze_node(state: AgentState) -> dict:
    """Nó de análise estatística avançada."""
    if state.get("error"):
        return {}

    df = state["raw_data"]
    if df is None:
        return {"error": "Nenhum dado disponível para análise"}

    correlations = _find_high_correlations(df)
    outliers = _detect_outliers_iqr(df)
    distributions = _get_distributions(df)
    numeric_profile = _compute_numeric_profile(df)
    business_metrics = _compute_business_metrics(df)

    # Análise temporal
    date_col = _detect_date_column(df)
    temporal = _analyze_temporal(df, date_col) if date_col else {}

    # Segmentação
    segments = _analyze_segments(df)

    # Padrões (agora com contexto completo)
    patterns = _detect_patterns(df, correlations, temporal, segments, business_metrics)

    statistical_analysis = {
        "high_correlations": correlations,
        "outliers": outliers,
        "distributions": distributions,
        "numeric_profile": numeric_profile,
        "temporal": temporal,
        "segments": segments,
        "business_metrics": business_metrics,
    }

    return {
        "statistical_analysis": statistical_analysis,
        "patterns": patterns,
    }
