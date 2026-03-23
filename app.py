"""Frontend Streamlit para o Deep Agent — Dark Mode com autenticacao por perfis."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from deep_agent.chains.qa import qa_node
from deep_agent.graph import build_graph

# ── Config da pagina ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Deep Agent",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background-color: #1a1d21; }

    section[data-testid="stSidebar"] {
        background-color: #13151a;
        border-right: 1px solid #2d2f36;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #2d2f36, #23252b);
        border: 1px solid #3a3d45;
        border-radius: 12px;
        padding: 16px;
        transition: border-color 0.2s;
    }
    div[data-testid="stMetric"]:hover { border-color: #7B68EE; }
    div[data-testid="stMetric"] label {
        color: #b0b4c0 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #e8e8e8 !important;
        font-size: 1.8rem !important;
        font-weight: 700;
    }

    details {
        background-color: #23252b !important;
        border: 1px solid #3a3d45 !important;
        border-radius: 10px !important;
    }
    details summary { color: #c8cad0 !important; }

    .stDataFrame { border-radius: 10px; overflow: hidden; }

    div[data-testid="stChatMessage"] {
        background-color: #23252b;
        border: 1px solid #3a3d45;
        border-radius: 12px;
        margin-bottom: 8px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #7B68EE, #6C5CE7);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 1.5rem; font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6C5CE7, #5A4BD1);
        box-shadow: 0 4px 15px rgba(123, 104, 238, 0.3);
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #00C897, #00B386);
        border: none; border-radius: 8px; color: white; font-weight: 600;
    }
    .stDownloadButton > button:hover { box-shadow: 0 4px 15px rgba(0, 200, 151, 0.3); }

    section[data-testid="stFileUploader"] {
        border: 2px dashed #3a3d45; border-radius: 12px; padding: 8px;
    }
    section[data-testid="stFileUploader"]:hover { border-color: #7B68EE; }

    .section-header {
        background: linear-gradient(135deg, #2d2f36, #23252b);
        border: 1px solid #3a3d45; border-radius: 10px;
        padding: 12px 20px; margin: 16px 0 12px 0;
        font-size: 1rem; font-weight: 600; color: #c8cad0;
    }
    .kpi-card {
        background: linear-gradient(135deg, #2d2f36, #23252b);
        border: 1px solid #3a3d45; border-radius: 12px;
        padding: 20px; text-align: center;
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #7B68EE; }
    .kpi-label {
        font-size: 0.75rem; color: #b0b4c0;
        text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px;
    }
    hr { border-color: #2d2f36; }
    #MainMenu, footer { visibility: hidden; }

    .pattern-badge {
        background: #2d2f36; border-left: 3px solid #7B68EE;
        border-radius: 0 8px 8px 0; padding: 10px 16px;
        margin: 6px 0; color: #c8cad0; font-size: 0.9rem;
    }
    .pattern-badge.warning { border-left-color: #FBBF24; }
    .pattern-badge.success { border-left-color: #00C897; }
    .pattern-badge.danger { border-left-color: #EF4444; }

    .context-bar {
        background: #23252b; border: 1px solid #3a3d45;
        border-radius: 10px; padding: 10px 16px;
        color: #b0b4c0; font-size: 0.85rem;
        margin-bottom: 16px; display: flex; gap: 16px;
    }
    .context-bar strong { color: #e8e8e8; }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2f36; border-radius: 8px 8px 0 0;
        color: #b0b4c0; padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #23252b; color: #7B68EE; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Autenticacao ─────────────────────────────────────────────────────────────

AUTH_CONFIG_YAML = os.environ.get("AUTH_CONFIG_YAML", "")


@st.cache_resource
def _get_sheets_client(credentials_json: str):
    """Singleton do cliente gspread — criado uma unica vez entre reruns."""
    from deep_agent.sources.google_sheets import GoogleSheetsSource
    GoogleSheetsSource.init_client(credentials_json)
    return GoogleSheetsSource._singleton_client


def _setup_auth():
    """Configura e executa o fluxo de autenticacao.

    Retorna (authenticator, is_admin, username) ou para a execucao se nao autenticado.
    """
    if not AUTH_CONFIG_YAML:
        # Modo dev — sem autenticacao
        return None, True, "dev"

    import yaml
    import streamlit_authenticator as stauth

    try:
        config = yaml.safe_load(AUTH_CONFIG_YAML)
    except Exception as e:
        st.error(f"Erro ao carregar configuracao de autenticacao: {e}")
        st.stop()

    cookie_cfg = config.get("cookie", {})
    authenticator = stauth.Authenticate(
        config.get("credentials", {}),
        cookie_cfg.get("name", "deep_agent_auth"),
        cookie_cfg.get("key", "fallback-key-change-me"),
        cookie_cfg.get("expiry_days", 30),
    )

    authenticator.login()

    auth_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username", "")

    if auth_status is False:
        st.error("Usuario ou senha incorretos.")
        st.stop()
    elif auth_status is None:
        st.info("Por favor, faca login para acessar o Deep Agent.")
        st.stop()

    # Determinar role a partir do YAML de credenciais
    user_data = config.get("credentials", {}).get("usernames", {}).get(username, {})
    user_roles = user_data.get("roles", [])
    is_admin = "admin" in user_roles

    return authenticator, is_admin, username


authenticator, is_admin, current_username = _setup_auth()

# ── Plotly template ─────────────────────────────────────────────────────────

PLOTLY_LAYOUT = {
    "paper_bgcolor": "#23252b", "plot_bgcolor": "#23252b",
    "font": {"color": "#c8cad0", "family": "Inter, sans-serif"},
    "xaxis": {"gridcolor": "#3a3d45", "zerolinecolor": "#3a3d45"},
    "yaxis": {"gridcolor": "#3a3d45", "zerolinecolor": "#3a3d45"},
    "colorway": ["#7B68EE", "#00C897", "#FBBF24", "#EF4444", "#3B82F6", "#EC4899", "#F97316", "#06B6D4"],
    "margin": {"t": 40, "b": 30, "l": 40, "r": 20},
}
COLORS = ["#7B68EE", "#00C897", "#FBBF24", "#EF4444", "#3B82F6", "#EC4899", "#F97316", "#06B6D4"]

MAX_CHAT_HISTORY = 50

# ── Estado global ───────────────────────────────────────────────────────────

for key, default in [("df", None), ("agent_state", None), ("chat_history", []),
                      ("report_text", None), ("file_path_tmp", None), ("data_source", None),
                      ("source_name", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ─────────────────────────────────────────────────────────────────


def _cleanup_tmp():
    p = st.session_state.get("file_path_tmp")
    if p and os.path.exists(p):
        try:
            os.unlink(p)
        except OSError:
            pass


def save_uploaded_file(f) -> str:
    _cleanup_tmp()
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(f.name).suffix) as tmp:
        tmp.write(f.getvalue())
        return tmp.name


def run_pipeline(file_path=None, data_source=None) -> dict:
    graph = build_graph()
    return graph.invoke({"file_path": file_path, "data_source": data_source, "mode": "report", "user_question": None})


def run_qa(state: dict, question: str) -> str:
    try:
        result = qa_node({**state, "user_question": question, "mode": "qa"})
        return result.get("qa_answer", "Sem resposta.")
    except Exception as e:
        return f"Erro ao consultar o LLM: {e}"


def run_report(file_path=None, data_source=None) -> dict:
    try:
        graph = build_graph()
        return graph.invoke({"file_path": file_path, "data_source": data_source, "mode": "report", "user_question": None})
    except Exception as e:
        return {"error": f"Erro ao gerar relatorio: {e}"}


def _check_api_key() -> bool:
    prov = os.environ.get("LLM_PROVIDER", "anthropic")
    key = os.environ.get("OPENAI_API_KEY", "") if prov == "openai" else os.environ.get("ANTHROPIC_API_KEY", "")
    return bool(key and len(key) > 10)


def _badge(text: str) -> str:
    cls = "pattern-badge"
    lo = text.lower()
    if any(w in lo for w in ["nulo", "zero", "decrescente", "baixa"]):
        cls += " danger"
    elif any(w in lo for w in ["crescente", "alta", "forte"]):
        cls += " success"
    elif any(w in lo for w in ["concentra", "pareto", "correlacao"]):
        cls += " warning"
    return f'<div class="{cls}">{text}</div>'


def _section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def _context_bar():
    if st.session_state.df is not None:
        d = st.session_state.df
        name = st.session_state.get("source_name", "Dataset")
        st.markdown(
            f'<div class="context-bar">'
            f'<span>📊 <strong>{name}</strong></span>'
            f'<span>{len(d):,} linhas x {len(d.columns)} colunas</span>'
            f'<span>{len(d.select_dtypes("number").columns)} numericas | {len(d.select_dtypes(["object","category"]).columns)} categoricas</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔮 Deep Agent")
    st.caption("Analista de Dados com IA")

    # Exibe usuario logado e botao de logout
    if authenticator is not None:
        user_name = st.session_state.get("name", current_username)
        role_label = "Admin" if is_admin else "Usuario"
        st.caption(f"👤 {user_name} · {role_label}")
        authenticator.logout(button_name="Sair", location="sidebar")
    st.markdown("---")

    # Fontes de dados — admin ve todas, user ve apenas arquivo
    if is_admin:
        source_options = ["📄 Arquivo", "📗 Google Sheets", "🗄️ Supabase", "📊 BigQuery"]
    else:
        source_options = ["📄 Arquivo"]

    source_type = st.radio("Fonte", source_options, label_visibility="collapsed")
    st.markdown("")

    def _load(source_id: str, source_name: str, **kwargs):
        if st.session_state.get("_source_id") == source_id:
            return
        st.session_state._source_id = source_id
        st.session_state.chat_history = []
        st.session_state.report_text = None
        st.session_state.source_name = source_name

        with st.status("Carregando dados...", expanded=True) as status:
            st.write("Conectando a fonte...")
            result = run_pipeline(**kwargs)
            if result.get("error"):
                status.update(label="Erro na conexao", state="error")
                st.error(result["error"])
                return
            st.write("Analisando padroes e metricas...")
            st.session_state.df = result["raw_data"]
            st.session_state.agent_state = result
            st.session_state.data_source = kwargs.get("data_source")
            rows = len(result["raw_data"])
            cols = len(result["raw_data"].columns)
            status.update(label=f"Pronto — {rows:,} linhas x {cols} colunas", state="complete")

    if source_type == "📄 Arquivo":
        f = st.file_uploader("Envie CSV ou Excel", type=["csv", "xlsx", "xls"], help="Max 50MB")
        if f:
            fid = f"file_{f.name}_{f.size}"
            if st.session_state.get("_source_id") != fid:
                tmp = save_uploaded_file(f)
                st.session_state.file_path_tmp = tmp
                _load(fid, f.name, file_path=tmp)

    elif source_type == "📗 Google Sheets":
        from deep_agent.config import settings
        url = st.text_input("URL ou Sheet ID", placeholder="1BxiMVs0XRA5...")
        tab = st.text_input("Aba (opcional)", placeholder="Sheet1")
        if url and st.button("🔗 Conectar", key="gs", use_container_width=True):
            sid = url
            if "docs.google.com" in url:
                parts = url.split("/d/")
                if len(parts) > 1:
                    sid = parts[1].split("/")[0]
            if not settings.google_credentials_json:
                st.error("Configure GOOGLE_CREDENTIALS_JSON")
            else:
                from deep_agent.sources.google_sheets import GoogleSheetsSource
                # Garante singleton inicializado com @st.cache_resource
                _get_sheets_client(settings.google_credentials_json)
                _load(f"gs_{sid}", "Google Sheets", data_source=GoogleSheetsSource(sid, settings.google_credentials_json, tab))

    elif source_type == "🗄️ Supabase":
        from deep_agent.config import settings
        tbl = st.text_input("Tabela", placeholder="vendas")
        qry = st.text_input("Colunas (opcional)", placeholder="* ou id,nome,valor")
        if tbl and st.button("🔗 Conectar", key="sb", use_container_width=True):
            if not settings.supabase_url:
                st.error("Configure SUPABASE_URL e SUPABASE_KEY")
            else:
                from deep_agent.sources.supabase_source import SupabaseSource
                _load(f"sb_{tbl}", f"Supabase: {tbl}", data_source=SupabaseSource(tbl, settings.supabase_url, settings.supabase_key, qry or ""))

    elif source_type == "📊 BigQuery":
        from deep_agent.config import settings
        bq_mode = st.radio("Modo", ["Tabela", "SQL"], horizontal=True, key="bqm")
        tid = st.text_input("Table ID", placeholder="project.dataset.table") if bq_mode == "Tabela" else ""
        sql = st.text_area("SQL", placeholder="SELECT * FROM ... LIMIT 1000", height=80) if bq_mode == "SQL" else ""
        if (tid or sql) and st.button("🔗 Conectar", key="bq", use_container_width=True):
            if not settings.gcp_project_id:
                st.error("Configure GCP_PROJECT_ID")
            else:
                from deep_agent.sources.bigquery import BigQuerySource
                _load(f"bq_{tid or hash(sql)}", "BigQuery", data_source=BigQuerySource(settings.gcp_project_id, tid, sql))

    st.markdown("---")
    page = st.radio("", ["📈 Dashboard", "💬 Chat", "📄 Relatorio"], label_visibility="collapsed")
    st.markdown("---")
    prov = os.environ.get("LLM_PROVIDER", "anthropic")
    mdl = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o") if prov == "openai" else os.environ.get("MODEL_NAME", "claude")
    st.caption(f"LLM: **{mdl}** | LangGraph")

# ── Main ────────────────────────────────────────────────────────────────────

df = st.session_state.df
state = st.session_state.agent_state

if df is None:
    st.markdown("# 🔮 Deep Agent")
    st.markdown("##### Analise dados com Inteligencia Artificial em 3 passos")
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="kpi-card"><div class="kpi-value">1</div><div class="kpi-label">Conecte seus dados</div><p style="color:#b0b4c0;font-size:0.85rem;margin-top:8px;">CSV, Excel, Google Sheets, Supabase ou BigQuery</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-card"><div class="kpi-value">2</div><div class="kpi-label">Explore o Dashboard</div><p style="color:#b0b4c0;font-size:0.85rem;margin-top:8px;">Metricas, graficos, correlacoes e padroes automaticos</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi-card"><div class="kpi-value">3</div><div class="kpi-label">Pergunte a IA</div><p style="color:#b0b4c0;font-size:0.85rem;margin-top:8px;">Chat inteligente ou relatorio completo com insights</p></div>', unsafe_allow_html=True)

    st.markdown("")
    st.info("👈 Selecione uma fonte de dados na barra lateral para comecar.")
    st.stop()

# ── Context bar ─────────────────────────────────────────────────────────────
_context_bar()

summary = state.get("data_summary", {})
stats = state.get("statistical_analysis", {})
patterns = state.get("patterns", [])
business = stats.get("business_metrics", {})
temporal = stats.get("temporal", {})
segments = stats.get("segments", {})
shape = summary.get("shape", {})
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

if page == "📈 Dashboard":
    if business:
        kc = st.columns(4)
        kpis = [
            ("Total Vendas", f"R$ {business.get('total_vendas', 0):,.2f}"),
            ("Total Lucro", f"R$ {business.get('total_lucro', 0):,.2f}"),
            ("Margem", f"{business.get('margem_lucro_pct', 0):.1f}%"),
            ("Ticket Medio", f"R$ {business.get('ticket_medio', 0):,.2f}"),
        ]
        for i, (label, val) in enumerate(kpis):
            if "0.00" not in str(val) and "0.0%" not in str(val):
                kc[i].metric(label, val)
        st.caption(f"{shape.get('rows',0):,} linhas x {shape.get('columns',0)} colunas | {len(numeric_cols)} numericas, {len(categorical_cols)} categoricas")
    else:
        kc = st.columns(4)
        kc[0].metric("Linhas", f"{shape.get('rows', 0):,}")
        kc[1].metric("Colunas", f"{shape.get('columns', 0)}")
        kc[2].metric("Numericas", f"{len(numeric_cols)}")
        kc[3].metric("Categoricas", f"{len(categorical_cols)}")

    tab_names = ["Visao Geral", "Analise"]
    if temporal and temporal.get("growth"):
        tab_names.append("Temporal")
    if segments:
        tab_names.append("Segmentos")

    tabs = st.tabs(tab_names)

    with tabs[0]:
        _section("🔍 Preview dos Dados")
        st.dataframe(df.head(100), use_container_width=True, height=400)

        if patterns:
            _section("🧩 Padroes Detectados")
            for p in patterns:
                st.markdown(_badge(p), unsafe_allow_html=True)

        null_counts = df.isnull().sum()
        null_counts = null_counts[null_counts > 0]
        if len(null_counts) > 0:
            with st.expander(f"❌ Valores Nulos ({len(null_counts)} colunas)"):
                null_df = pd.DataFrame({"Coluna": null_counts.index, "Nulos": null_counts.values, "%": (null_counts.values / len(df) * 100).round(1)})
                st.dataframe(null_df, use_container_width=True, hide_index=True)

        with st.expander("📐 Estatisticas Descritivas"):
            st.dataframe(df.describe(include="all").T, use_container_width=True)

    with tabs[1]:
        if numeric_cols:
            _section("📊 Distribuicoes")
            sel = st.multiselect("Colunas", numeric_cols, default=numeric_cols[:3], key="dist_cols")
            if sel:
                cols = st.columns(min(len(sel), 3))
                for i, cn in enumerate(sel):
                    with cols[i % 3]:
                        fig = px.histogram(df, x=cn, title=cn, color_discrete_sequence=[COLORS[i % len(COLORS)]])
                        fig.update_layout(height=280, showlegend=False, **PLOTLY_LAYOUT)
                        st.plotly_chart(fig, use_container_width=True)

            cl, cr = st.columns(2)
            with cl:
                _section("🔎 Box Plot")
                bx = st.selectbox("Coluna", numeric_cols, key="bx")
                fig = px.box(df, y=bx, color_discrete_sequence=["#EF4444"])
                fig.update_layout(height=320, **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)
            with cr:
                _section("📐 Perfil Numerico")
                prof = stats.get("numeric_profile", {})
                if prof:
                    st.dataframe(pd.DataFrame(prof).T.rename_axis("Coluna"), use_container_width=True, height=320)

            outliers = stats.get("outliers", {})
            if outliers:
                with st.expander(f"⚠️ Outliers ({len(outliers)} colunas)"):
                    rows = []
                    for c, info in outliers.items():
                        if isinstance(info, dict):
                            rows.append({"Coluna": c, "Qtd": info["count"], "Lim.Inf": info["lower_bound"], "Lim.Sup": info["upper_bound"], "Min": info["min_outlier"], "Max": info["max_outlier"]})
                        else:
                            rows.append({"Coluna": c, "Qtd": info})
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        if numeric_cols and len(numeric_cols) >= 2:
            with st.expander("🔗 Matriz de Correlacao", expanded=len(numeric_cols) <= 8):
                corr = df[numeric_cols].corr()
                fig = px.imshow(corr, text_auto=".2f", color_continuous_scale=["#EF4444", "#23252b", "#7B68EE"])
                fig.update_layout(height=450, **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        if categorical_cols:
            _section("📋 Distribuicoes Categoricas")
            cc = st.selectbox("Coluna", categorical_cols, key="cc")
            vc = df[cc].value_counts().head(15)
            fig = px.bar(x=vc.index.astype(str), y=vc.values, labels={"x": cc, "y": "Contagem"}, color_discrete_sequence=["#00C897"])
            fig.update_layout(height=320, **PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    if temporal and temporal.get("growth") and len(tabs) > 2:
        with tabs[2]:
            st.caption(f"Periodo: **{temporal.get('date_range', '')}** | {temporal.get('period_count', 0)} periodos")

            pt = temporal.get("period_totals", {})
            if pt:
                sel_t = st.selectbox("Metrica", list(pt.keys()), key="ts")
                periods = list(pt[sel_t].keys())
                vals = list(pt[sel_t].values())
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=periods, y=vals, mode="lines+markers",
                    line=dict(color="#7B68EE", width=3), marker=dict(size=8),
                    fill="tozeroy", fillcolor="rgba(123,104,238,0.1)"))
                fig.update_layout(title=f"Evolucao: {sel_t}", height=380, **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            growth = temporal.get("growth", {})
            if growth:
                gc = st.columns(min(len(growth), 4))
                for i, (c, g) in enumerate(growth.items()):
                    icon = "📈" if g["trend"] == "crescente" else "📉" if g["trend"] == "decrescente" else "➡️"
                    gc[i % 4].metric(c, f"{g['avg_growth_pct']:+.1f}%", delta=f"{icon} {g['trend']}")

    if segments and len(tabs) > (3 if temporal and temporal.get("growth") else 2):
        with tabs[-1]:
            sc = st.selectbox("Segmentar por", list(segments.keys()), key="sg")
            agg = segments[sc].get("aggregation", {})
            skeys = [k for k in agg.keys() if k.endswith("_sum")]
            if skeys:
                sm = st.selectbox("Metrica", skeys, format_func=lambda x: x.replace("_sum", ""), key="sm")
                v = agg[sm]
                fig = px.bar(x=list(v.keys()), y=list(v.values()), labels={"x": sc, "y": sm.replace("_sum", "")}, color_discrete_sequence=[COLORS[0]])
                fig.update_layout(height=380, **PLOTLY_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# CHAT
# ═══════════════════════════════════════════════════════════════════════════

elif page == "💬 Chat":
    st.markdown("# 💬 Chat com seus Dados")

    if not _check_api_key():
        st.warning("Configure a API key do LLM para usar o chat.")

    hcol1, hcol2 = st.columns([8, 2])
    with hcol2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if not st.session_state.chat_history:
        st.caption("Sugestoes baseadas nos seus dados:")
        suggestions = []
        if business:
            suggestions.append("Qual a margem de lucro por segmento?")
        if temporal and temporal.get("growth"):
            suggestions.append("Qual a tendencia de crescimento?")
        if numeric_cols:
            suggestions.append(f"Quais outliers existem em '{numeric_cols[0]}'?")
        if categorical_cols:
            suggestions.append(f"Como se distribui '{categorical_cols[0]}'?")
        if not suggestions:
            suggestions = ["Resuma os principais insights dos dados", "Quais padroes voce identifica?"]

        scols = st.columns(min(len(suggestions), 2))
        for i, s in enumerate(suggestions):
            with scols[i % 2]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": s})
                    with st.spinner("Analisando..."):
                        answer = run_qa(state, s)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Faca uma pergunta sobre seus dados..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                answer = run_qa(state, prompt)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        if len(st.session_state.chat_history) > MAX_CHAT_HISTORY:
            st.session_state.chat_history = st.session_state.chat_history[-MAX_CHAT_HISTORY:]


# ═══════════════════════════════════════════════════════════════════════════
# RELATORIO
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📄 Relatorio":
    st.markdown("# 📄 Relatorio com Insights de IA")

    if st.session_state.report_text:
        st.markdown(st.session_state.report_text)

        dc1, dc2 = st.columns(2)
        with dc1:
            st.download_button("⬇️ Download Relatorio (.md)", st.session_state.report_text, "relatorio_deep_agent.md", "text/markdown")
        with dc2:
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download Dados (.csv)", csv, "dados_analisados.csv", "text/csv")
    else:
        if not _check_api_key():
            st.warning("Configure a API key do LLM para gerar relatorios.")

        st.info(f"Gere um relatorio completo com insights de IA sobre **{shape.get('rows',0):,} linhas** e **{shape.get('columns',0)} colunas** de dados.")

        if st.button("🚀 Gerar Relatorio", type="primary", use_container_width=True):
            with st.status("Gerando relatorio...", expanded=True) as status:
                st.write("Carregando dados...")
                st.write("Analisando padroes e metricas...")
                st.write("Gerando insights com IA...")
                result = run_report(
                    file_path=st.session_state.get("file_path_tmp"),
                    data_source=st.session_state.get("data_source"),
                )
                if result.get("error"):
                    status.update(label="Erro", state="error")
                    st.error(result["error"])
                elif result.get("report"):
                    st.session_state.report_text = result["report"]
                    st.session_state.agent_state = result
                    status.update(label="Relatorio pronto!", state="complete")
                    st.rerun()
                else:
                    status.update(label="Falha", state="error")
                    st.warning("Relatorio nao gerado. Verifique a API key.")
