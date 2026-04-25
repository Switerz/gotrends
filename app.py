"""
Kokeshi · Google Ads Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from datetime import date, datetime
from auth import login_required

BASE = Path(__file__).parent
TICKET_MEDIO = 90.0
CPA_GREAT = 20.0
CPA_WARN = 40.0
CPA_CRITICAL = 50.0
BRAND_RED = "#B42828"

CAMPAIGN_TYPE_LABELS = {
    "BRANDED": "Marca",
    "NON_BRANDED": "Não Marca",
    "SEARCH_NON_BRANDED": "Não Marca",
    "PERFORMANCE_MAX": "Performance Max",
    "PMAX": "Performance Max",
    "DISPLAY": "Display",
    "SHOPPING": "Shopping",
    "VIDEO": "Vídeo",
    "OTHER": "Outros",
}

CAMPAIGN_COLORS = {
    "Marca": "#B42828",
    "Não Marca": "#1565C0",
    "Performance Max": "#6A1B9A",
    "Display": "#E65100",
    "Shopping": "#2E7D32",
    "Vídeo": "#00838F",
    "Outros": "#9E9E9E",
}

ACTION_LABELS = {
    "ESCALAR":                    ("🚀 Escalar termos com CPA baixo",            "#2E7D32"),
    "CRIAR_KEYWORD_EXATA":        ("🎯 Criar keywords exatas de alta conversão",  "#1565C0"),
    "SUGERIR_NEGATIVA":           ("🚫 Negativar termos ineficientes",            "#B42828"),
    "CORTAR_OU_NEGATIVAR":        ("✂️ Cortar termos com CPA inviável",           "#B42828"),
    "REVISAR_URGENTE":            ("⚠️ Revisar termos com CPA alto",              "#E65100"),
    "REVISAR_OU_NEGATIVAR":       ("🔍 Revisar ou negativar concorrentes",        "#F9A825"),
    "CRIAR_CONTEUDO_OU_LANDING":  ("📄 Criar conteúdo ou landing page",           "#6A1B9A"),
}

INTENT_COLORS = {
    "COMPRADOR": "#1565C0",
    "PESQUISADOR": "#2E7D32",
    "COMPARADOR": "#E65100",
    "CAÇADOR_DE_BRINDE": "#E65100",
    "CONCORRENTE/MARCA_TERCEIRA": "#6A1B9A",
    "INTENÇÃO_AMBÍGUA": "#9E9E9E",
}

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kokeshi · Google Ads",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="auto",
)

login_required()  # bloqueia tudo abaixo se não estiver autenticado

st.markdown("""
<style>
[data-testid="stMetricValue"]  { font-size: 1.45rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"]  { font-size: 0.70rem !important; color: #666 !important; }
[data-testid="stMetricDelta"]  { font-size: 0.72rem !important; }

.health-badge {
    display: inline-block; padding: 6px 16px; border-radius: 20px;
    font-weight: 700; font-size: 1.05rem; margin-bottom: 4px;
}
.health-green  { background: #E8F5E9; color: #2E7D32; border: 1.5px solid #2E7D32; }
.health-yellow { background: #FFFDE7; color: #F57F17; border: 1.5px solid #F9A825; }
.health-red    { background: #FFEBEE; color: #B71C1C; border: 1.5px solid #B42828; }

.insight-box {
    background: #F3F4F6; border-left: 4px solid #B42828;
    padding: 10px 16px; border-radius: 4px; margin: 8px 0 16px 0;
    font-size: 0.90rem; color: #1a1a1a;
}

.opp-card-scale {
    background: #F0FFF4; border-left: 4px solid #22863A;
    padding: 10px 14px; border-radius: 4px; margin-bottom: 8px;
}
.opp-card-cut {
    background: #FFF8E1; border-left: 4px solid #F9A825;
    padding: 10px 14px; border-radius: 4px; margin-bottom: 8px;
}
.opp-value-green { font-size: 1.4rem; font-weight: 700; color: #22863A; }
.opp-value-amber { font-size: 1.4rem; font-weight: 700; color: #E65100; }
.opp-label { font-size: 0.80rem; color: #333; margin-bottom: 2px; font-weight: 600; }
.opp-sub   { font-size: 0.72rem; color: #888; margin-top: 3px; }

.action-card {
    border-left: 4px solid #ccc; background: #FAFAFA;
    padding: 10px 14px; border-radius: 4px; margin-bottom: 8px;
}
.action-card-alta   { border-left-color: #B42828; }
.action-card-media  { border-left-color: #F9A825; }
.action-card-baixa  { border-left-color: #9E9E9E; }
.action-term  { font-weight: 700; font-size: 0.88rem; }
.action-meta  { font-size: 0.72rem; color: #666; margin: 3px 0; }
.action-reason { font-size: 0.78rem; color: #333; margin-top: 4px; }

.kw-card {
    border-left: 4px solid #ccc; background: #F8F9FA;
    padding: 10px 14px; border-radius: 4px; margin-bottom: 8px;
}
.kw-term  { font-weight: 700; font-size: 0.88rem; }
.kw-meta  { font-size: 0.72rem; color: #666; margin-top: 3px; }
.kw-score { font-size: 0.72rem; color: #888; margin-top: 2px; }

.empty-state {
    text-align: center; padding: 40px 20px; color: #888;
    border: 2px dashed #ddd; border-radius: 8px; margin: 20px 0;
}
.empty-state h3 { color: #555; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_brl(v, decimals=0) -> str:
    if v is None or (isinstance(v, float) and (pd.isna(v) or np.isnan(v))):
        return "—"
    s = f"{float(v):,.{decimals}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$" + s


def fmt_x(v, decimals=1) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{float(v):,.{decimals}f}x".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{float(v)*100:.1f}%"


def last_modified(filename: str) -> str:
    p = BASE / filename
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%d/%m %H:%M") if p.exists() else "—"


def label_type(t: str) -> str:
    return CAMPAIGN_TYPE_LABELS.get(str(t).upper(), t)


def color_for_type(label: str) -> str:
    return CAMPAIGN_COLORS.get(label, "#9E9E9E")


# ── Data loaders ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_csv(name: str) -> pd.DataFrame:
    p = BASE / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def load_terms_analysis() -> pd.DataFrame:
    from tools.google_ads_growth_engine import analyze_terms, add_business_context
    df = load_csv("google_ads_search_terms.csv")
    if df.empty:
        return pd.DataFrame()
    df = add_business_context(df)
    return analyze_terms(df)


def to_num(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def compute_kpis(df_c: pd.DataFrame, df_t: pd.DataFrame) -> dict:
    if df_c.empty:
        return {}
    df_c = to_num(df_c.copy(), ["cost", "conversions", "cpa"])
    total_cost = float(df_c["cost"].sum())
    total_conv = float(df_c["conversions"].sum())
    cpa = total_cost / total_conv if total_conv > 0 else None
    revenue = total_conv * TICKET_MEDIO
    roas = revenue / total_cost if total_cost > 0 else None

    scale_upside, wasted_40, forecast_base = 0, 0, None
    if not df_t.empty and cpa:
        df_t = to_num(df_t.copy(), ["cost", "conversions", "cpa"])
        bad = df_t[df_t["cpa"].notna() & (df_t["cpa"] > 40)]
        wasted_40 = float(bad["cost"].fillna(0).sum())
        forecast_base = round((wasted_40 * 0.75) / cpa * TICKET_MEDIO, 2) if cpa else None
        scale = df_t[df_t["cpa"].notna() & (df_t["cpa"] <= 15) & (df_t["conversions"].fillna(0) >= 2)]
        scale_upside = round(float(scale["cost"].sum() * 0.5 / cpa * TICKET_MEDIO), 2) if not scale.empty else 0

    return {
        "total_cost": round(total_cost, 2),
        "total_conversions": round(total_conv, 2),
        "cpa": round(cpa, 2) if cpa else None,
        "revenue": round(revenue, 2),
        "roas": round(roas, 2) if roas else None,
        "wasted_40": round(wasted_40, 2),
        "scale_upside": scale_upside,
        "forecast_base": forecast_base,
        "campaigns_count": int(len(df_c)),
    }


def account_health(cpa) -> tuple[str, str, str]:
    """Returns (emoji+label, css_class, headline_insight)."""
    if cpa is None:
        return "— Sem dados", "health-yellow", "Sem dados suficientes para avaliação."
    if cpa <= 15:
        return "🟢 Saudável", "health-green", "CPA excelente — a maior alavanca agora é escalar branded com segurança."
    if cpa <= 25:
        return "🟡 Atenção", "health-yellow", "CPA dentro do limite, mas há termos acima de R$40 a cortar."
    return "🔴 Crítico", "health-red", "CPA acima do benchmark — prioridade: negativar termos ineficientes."


# ── Header ─────────────────────────────────────────────────────────────────────
hc1, hc2, hc3 = st.columns([5, 3, 1])
with hc1:
    st.markdown(f"<h2 style='margin:0;color:{BRAND_RED}'>🌸 Kokeshi · Google Ads</h2>",
                unsafe_allow_html=True)
with hc2:
    st.caption(f"Dados: {last_modified('google_ads_search_terms.csv')} · Ticket médio R$90")
with hc3:
    if st.button("↺ Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ── Load once ──────────────────────────────────────────────────────────────────
with st.spinner("Carregando dados..."):
    df_terms     = load_terms_analysis()
    df_campaigns = load_csv("campaign_constraints_analysis.csv")
    df_organic   = load_csv("paid_organic_opportunity_analysis.csv")
    df_kw_new    = load_csv("new_keyword_suggestions.csv")

kpis = compute_kpis(df_campaigns, df_terms.copy() if not df_terms.empty else pd.DataFrame())

# ── Tabs ───────────────────────────────────────────────────────────────────────
t_exec, t_actions, t_campaigns, t_organic_tab, t_kw, t_launches = st.tabs([
    "📊 Resumo Executivo",
    "⚡ Ações Prioritárias",
    "📈 Campanhas",
    "🔍 Pago vs Orgânico",
    "💡 Novas Keywords",
    "🚀 Lançamentos",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESUMO EXECUTIVO
# ══════════════════════════════════════════════════════════════════════════════
with t_exec:
    today = date.today()
    dias_maio = (date(2026, 5, 1) - today).days
    if dias_maio <= 45:
        st.warning(
            f"⚠️ **Lançamentos iminentes:** Sérum Roll on Adeus Olheiras (este mês) + "
            f"4 produtos em mai/26 **({dias_maio} dias)**. Keywords ainda não criadas. Ver aba Lançamentos."
        )

    # Health badge + insight
    health_label, health_css, insight_text = account_health(kpis.get("cpa"))
    hb1, hb2 = st.columns([1, 4])
    with hb1:
        st.markdown(f'<div class="health-badge {health_css}">{health_label}</div>',
                    unsafe_allow_html=True)
    with hb2:
        st.markdown(f'<div class="insight-box">💡 {insight_text}</div>',
                    unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💸 Custo Total",    fmt_brl(kpis.get("total_cost")))
    k2.metric("🎯 Conversões",     f"{kpis.get('total_conversions', 0):,.0f}".replace(",", "."))
    k3.metric("📉 CPA Médio",      fmt_brl(kpis.get("cpa"), 2))
    k4.metric("💰 Receita Est.",   fmt_brl(kpis.get("revenue")))
    k5.metric("📈 ROAS",           fmt_x(kpis.get("roas")))

    st.divider()

    col_opp, col_chart = st.columns(2)

    # — Oportunidade financeira —
    with col_opp:
        st.subheader("Oportunidade Financeira")
        scale = kpis.get("scale_upside", 0) or 0
        fb    = kpis.get("forecast_base", 0) or 0
        wasted = kpis.get("wasted_40", 0) or 0
        st.markdown(f"""
        <div class="opp-card-scale">
            <div class="opp-label">🚀 Ganho Potencial — escalar winners (CPA ≤ R$15)</div>
            <div class="opp-value-green">{fmt_brl(scale)}</div>
            <div class="opp-sub">+50% de spend nos melhores termos ao CPA médio da conta</div>
        </div>
        <div class="opp-card-cut">
            <div class="opp-label">✂️ Economia Potencial — cortar desperdício (CPA &gt; R$40)</div>
            <div class="opp-value-amber">{fmt_brl(fb)}</div>
            <div class="opp-sub">{fmt_brl(wasted)} identificados · cenário base de realocação</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Escalar é a alavanca dominante — razão ~10:1 sobre corte de desperdício.")

    # — Donut: spend por tipo (sem zeros, maior slice em destaque) —
    with col_chart:
        if not df_campaigns.empty and "campaign_type" in df_campaigns.columns:
            dc = to_num(df_campaigns.copy(), ["cost", "conversions"])
            dc["type_label"] = dc["campaign_type"].apply(label_type)
            grp = dc.groupby("type_label")[["cost", "conversions"]].sum().reset_index()
            grp = grp[grp["cost"] > 0].sort_values("cost", ascending=False)
            grp["conversions"] = grp["conversions"].fillna(0)
            grp["revenue"] = grp["conversions"] * TICKET_MEDIO
            grp["roas"]    = np.where(grp["cost"] > 0, (grp["revenue"] / grp["cost"]).round(2), 0)
            grp["color"]   = grp["type_label"].apply(color_for_type)
            # pull apenas o maior slice
            pull = [0.09 if i == 0 else 0.0 for i in range(len(grp))]

            fig_donut = go.Figure(go.Pie(
                labels=grp["type_label"],
                values=grp["cost"],
                hole=0.52,
                pull=pull,
                marker=dict(
                    colors=grp["color"].tolist(),
                    line=dict(color="#fff", width=2),
                ),
                textinfo="percent+label",
                textposition="inside",
                insidetextorientation="radial",
                textfont=dict(size=11, color="#fff"),
                customdata=grp[["revenue", "roas", "conversions"]].values,
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Spend: R$%{value:,.0f}<br>"
                    "Receita: R$%{customdata[0]:,.0f}<br>"
                    "ROAS: %{customdata[1]:.1f}x<br>"
                    "Conversões: %{customdata[2]:,.0f}<extra></extra>"
                ),
                sort=False,
            ))
            fig_donut.update_layout(
                title=dict(text="Spend por Tipo", font=dict(size=13)),
                height=240,
                margin=dict(t=36, b=0, l=0, r=0),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_donut, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — AÇÕES PRIORITÁRIAS
# ══════════════════════════════════════════════════════════════════════════════
with t_actions:
    if df_terms.empty:
        st.warning("google_ads_search_terms.csv não encontrado. Rode `python export_google_ads_search_terms.py`.")
    else:
        f1, f2, f3, f4 = st.columns(4)
        filt = df_terms.copy()

        opts_p = ["Todas"] + sorted(filt["priority"].dropna().unique().tolist())
        opts_a = ["Todas"] + sorted(filt["action"].dropna().unique().tolist())
        opts_t = ["Todos"] + sorted(filt["campaign_type"].dropna().unique().tolist())
        opts_i = ["Todas"] + sorted(filt["search_intent"].dropna().unique().tolist())

        sel_p = f1.selectbox("Prioridade", opts_p, key="a_p")
        sel_a = f2.selectbox("Ação",       opts_a, key="a_a")
        sel_t = f3.selectbox("Tipo",       opts_t, key="a_t")
        sel_i = f4.selectbox("Intenção",   opts_i, key="a_i")

        if sel_p != "Todas":  filt = filt[filt["priority"]      == sel_p]
        if sel_a != "Todas":  filt = filt[filt["action"]         == sel_a]
        if sel_t != "Todos":  filt = filt[filt["campaign_type"]  == sel_t]
        if sel_i != "Todas":  filt = filt[filt["search_intent"]  == sel_i]
        if sel_a == "Todas":  filt = filt[filt["action"]         != "MANTER"]

        filt = to_num(filt, ["cost", "conversions", "cpa", "revenue_estimate", "roas_estimate"])
        st.caption(f"{len(filt)} termos com ação recomendada")

        # ── Tabela compacta (sem reason) ──
        cols_tbl = ["search_term", "campaign_type", "search_intent",
                    "cost", "conversions", "cpa", "action", "priority"]
        cols_ok  = [c for c in cols_tbl if c in filt.columns]
        disp = filt[cols_ok].copy()
        disp["cost"] = disp["cost"].apply(lambda x: fmt_brl(x, 2) if pd.notna(x) else "—")
        if "cpa" in disp.columns:
            disp["cpa"]  = disp["cpa"].apply(lambda x: fmt_brl(x, 2) if pd.notna(x) else "—")

        st.dataframe(
            disp.head(100),
            use_container_width=True,
            hide_index=True,
            column_config={
                "search_term":   st.column_config.TextColumn("Termo",    width="medium"),
                "campaign_type": st.column_config.TextColumn("Tipo",     width="small"),
                "search_intent": st.column_config.TextColumn("Intenção", width="medium"),
                "cost":          st.column_config.TextColumn("Custo"),
                "conversions":   st.column_config.NumberColumn("Conv.", format="%.1f"),
                "cpa":           st.column_config.TextColumn("CPA"),
                "action":        st.column_config.TextColumn("Ação",     width="medium"),
                "priority":      st.column_config.TextColumn("Prior.",   width="small"),
            },
        )

        # ── Top 3 ações consolidadas ──
        alta = filt[filt["priority"] == "ALTA"] if "ALTA" in filt.get("priority", pd.Series()).values else filt
        if not alta.empty and "action" in alta.columns:
            st.markdown("##### O que fazer agora")
            groups = []
            for action_code, grp_df in alta.groupby("action"):
                total_cost = float(grp_df["cost"].fillna(0).sum())
                sample_reason = grp_df["reason"].dropna().iloc[0][:90] if "reason" in grp_df.columns and len(grp_df) > 0 else "—"
                sample_terms  = ", ".join(str(t) for t in grp_df["search_term"].head(3).tolist())
                groups.append({
                    "action": action_code,
                    "count":  len(grp_df),
                    "cost":   total_cost,
                    "reason": sample_reason,
                    "terms":  sample_terms,
                })
            groups.sort(key=lambda x: x["cost"], reverse=True)

            top3_cols = st.columns(min(3, len(groups)))
            for i, g in enumerate(groups[:3]):
                label, color = ACTION_LABELS.get(g["action"], (g["action"], "#666"))
                with top3_cols[i]:
                    st.markdown(f"""
                    <div style="border-left:4px solid {color};background:#FAFAFA;
                                padding:12px 14px;border-radius:4px;">
                        <div style="font-weight:700;font-size:0.86rem;color:{color}">{label}</div>
                        <div style="font-size:1.2rem;font-weight:700;color:#1a1a1a;margin:4px 0">
                            {fmt_brl(g['cost'])} em jogo
                        </div>
                        <div style="font-size:0.72rem;color:#666">{g['count']} termo(s) · ex: {g['terms'][:55]}</div>
                        <div style="font-size:0.75rem;color:#444;margin-top:6px">{g['reason']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if len(groups) > 3:
                remaining = len(groups) - 3
                with st.expander(f"Ver {remaining} categoria{'s' if remaining != 1 else ''} adicional{'is' if remaining != 1 else ''}"):
                    for g in groups[3:]:
                        label, color = ACTION_LABELS.get(g["action"], (g["action"], "#666"))
                        st.markdown(
                            f"**{label}** · {g['count']} termos · {fmt_brl(g['cost'])} · _{g['reason']}_"
                        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CAMPANHAS
# ══════════════════════════════════════════════════════════════════════════════
with t_campaigns:
    if df_campaigns.empty:
        st.warning("campaign_constraints_analysis.csv não encontrado.")
    else:
        dc = to_num(df_campaigns.copy(),
                    ["cost", "conversions", "cpa", "impressions",
                     "search_impression_share", "search_budget_lost_impression_share",
                     "search_rank_lost_impression_share"])

        show_inactive = st.toggle("Mostrar campanhas inativas (0 spend)", value=False)
        if not show_inactive:
            dc = dc[dc["cost"].fillna(0) > 0]

        dc["type_label"] = dc["campaign_type"].apply(label_type) if "campaign_type" in dc.columns else "—"

        # ── Gráfico IS — top 10 por perda de Ad Rank ──
        st.subheader("Impression Share — Top 10 por Perda de Ad Rank")

        if "search_impression_share" in dc.columns:
            df_is = dc[dc["search_impression_share"].notna() & (dc["search_impression_share"] > 0)].copy()
            df_is["IS %"]           = (df_is["search_impression_share"].fillna(0) * 100).round(1)
            df_is["Rank Lost %"]    = (df_is.get("search_rank_lost_impression_share", pd.Series(0, index=df_is.index)).fillna(0) * 100).round(1)
            df_is["Budget Lost %"]  = (df_is.get("search_budget_lost_impression_share", pd.Series(0, index=df_is.index)).fillna(0) * 100).round(1)
            df_is = df_is.sort_values("Rank Lost %", ascending=False).head(10).sort_values("Rank Lost %", ascending=True)

            if not df_is.empty:
                fig_is = go.Figure()
                fig_is.add_trace(go.Bar(
                    y=df_is["campaign_name"], x=df_is["IS %"],
                    orientation="h", name="IS Capturado",
                    marker_color=BRAND_RED,
                    hovertemplate="IS Capturado: %{x:.1f}%<extra></extra>",
                ))
                fig_is.add_trace(go.Bar(
                    y=df_is["campaign_name"], x=df_is["Rank Lost %"],
                    orientation="h", name="Perdido · Ad Rank",
                    marker_color="#F4A0A0",
                    hovertemplate="Perdido (Ad Rank): %{x:.1f}%<extra></extra>",
                ))
                fig_is.add_trace(go.Bar(
                    y=df_is["campaign_name"], x=df_is["Budget Lost %"],
                    orientation="h", name="Perdido · Orçamento",
                    marker_color="#FDD9D9",
                    hovertemplate="Perdido (Orçamento): %{x:.1f}%<extra></extra>",
                ))
                fig_is.update_layout(
                    barmode="stack", height=360,
                    margin=dict(t=10, b=10, l=10, r=10),
                    xaxis=dict(title="Impression Share %", range=[0, 100]),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig_is, use_container_width=True)
            else:
                st.info("Sem dados de Impression Share disponíveis.")

        # ── Matriz de quadrantes Custo vs Conversões ──
        st.subheader("Quadrantes: Custo vs Conversões")

        type_opts_q = ["Todos"] + sorted(dc["type_label"].dropna().unique().tolist()) if "type_label" in dc.columns else ["Todos"]
        sel_type_q  = st.selectbox("Filtrar por tipo de campanha", type_opts_q, key="q_type")

        df_q = dc.dropna(subset=["cost", "conversions"]).copy()
        df_q = df_q[df_q["cost"] > 0]
        if sel_type_q != "Todos" and "type_label" in df_q.columns:
            df_q = df_q[df_q["type_label"] == sel_type_q]

        if not df_q.empty:
            x_mid = float(df_q["cost"].median())
            y_mid = float(df_q["conversions"].median())

            def _quadrant(row):
                hi_c = row["cost"]        >= x_mid
                hi_v = row["conversions"] >= y_mid
                if hi_c and hi_v:     return "Escalar"
                if hi_c and not hi_v: return "Cortar"
                if not hi_c and hi_v: return "Oportunidade"
                return "Monitorar"

            df_q["Quadrante"]   = df_q.apply(_quadrant, axis=1)
            df_q["bubble_size"] = np.sqrt(df_q["cost"].clip(lower=1))
            if "cpa" not in df_q.columns:
                df_q["cpa"] = np.nan
            df_q["cpa_fmt"]  = df_q["cpa"].apply(lambda x: fmt_brl(x, 2) if pd.notna(x) else "—")
            df_q["roas_calc"] = (df_q["conversions"] * TICKET_MEDIO / df_q["cost"]).round(2)

            q_colors = {"Escalar": "#2E7D32", "Oportunidade": "#1565C0",
                        "Cortar": "#B42828",  "Monitorar":    "#9E9E9E"}

            fig_q = px.scatter(
                df_q, x="cost", y="conversions",
                color="Quadrante",
                color_discrete_map=q_colors,
                size="bubble_size",
                size_max=28,
                custom_data=["campaign_name", "cpa_fmt", "roas_calc"],
                labels={"cost": "Custo (R$)", "conversions": "Conversões"},
            )
            fig_q.update_traces(
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Custo: R$%{x:,.0f}<br>"
                    "Conversões: %{y:.1f}<br>"
                    "CPA: %{customdata[1]}<br>"
                    "ROAS: %{customdata[2]:.1f}x<extra></extra>"
                )
            )
            fig_q.add_vline(x=x_mid, line_dash="dot", line_color="#bbb",
                            annotation_text=f"Mediana custo R${x_mid:,.0f}",
                            annotation_position="top right", annotation_font_size=9)
            fig_q.add_hline(y=y_mid, line_dash="dot", line_color="#bbb",
                            annotation_text=f"Mediana {y_mid:.0f} conv",
                            annotation_position="bottom right", annotation_font_size=9)

            x_max = float(df_q["cost"].max())
            y_max = float(df_q["conversions"].max())
            for qtxt, tx, ty, clr in [
                ("ESCALAR ↗",      x_max * 0.88, y_max * 0.94, "#2E7D32"),
                ("CORTAR ↙",       x_max * 0.88, y_max * 0.06, "#B42828"),
                ("OPORTUNIDADE ↗", x_max * 0.04, y_max * 0.94, "#1565C0"),
                ("MONITORAR",      x_max * 0.04, y_max * 0.06, "#9E9E9E"),
            ]:
                fig_q.add_annotation(x=tx, y=ty, text=qtxt, showarrow=False,
                                     font=dict(size=9, color=clr, family="Arial Black"))

            # Labels nos top 5 por custo
            for _, row in df_q.nlargest(5, "cost").iterrows():
                name = str(row.get("campaign_name", ""))[:22]
                fig_q.add_annotation(
                    x=row["cost"], y=row["conversions"],
                    text=name, showarrow=True, arrowhead=2,
                    arrowsize=0.7, arrowcolor="#888", arrowwidth=1,
                    font=dict(size=8, color="#333"),
                    ax=18, ay=-18, bgcolor="rgba(255,255,255,0.8)",
                )

            fig_q.update_layout(
                height=380, margin=dict(t=10, b=20, l=10, r=10),
                plot_bgcolor="#FAFAFA", legend=dict(orientation="h", y=1.04),
            )
            st.plotly_chart(fig_q, use_container_width=True)

        # ── Tabela ──
        st.subheader("Tabela de Campanhas")
        tbl_cols = ["campaign_name", "type_label", "cost", "conversions", "cpa",
                    "search_impression_share", "search_rank_lost_impression_share",
                    "constraint_type"]
        tbl_ok = [c for c in tbl_cols if c in dc.columns]
        tbl = dc[tbl_ok].copy()

        if not show_inactive:
            low_vol = tbl["cost"].fillna(0) < 100
        for col in ["cost", "cpa"]:
            if col in tbl.columns:
                tbl[col] = tbl[col].apply(lambda x: fmt_brl(x, 2) if pd.notna(x) else "—")
        for col in ["search_impression_share", "search_rank_lost_impression_share"]:
            if col in tbl.columns:
                tbl[col] = pd.to_numeric(tbl[col], errors="coerce").apply(
                    lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
                )
        st.dataframe(tbl, use_container_width=True, hide_index=True,
                     column_config={
                         "campaign_name": st.column_config.TextColumn("Campanha",   width="large"),
                         "type_label":    st.column_config.TextColumn("Tipo",       width="small"),
                         "cost":          st.column_config.TextColumn("Custo"),
                         "conversions":   st.column_config.NumberColumn("Conv.", format="%.1f"),
                         "cpa":           st.column_config.TextColumn("CPA"),
                         "search_impression_share":           st.column_config.TextColumn("IS"),
                         "search_rank_lost_impression_share": st.column_config.TextColumn("Rank Lost"),
                         "constraint_type": st.column_config.TextColumn("Restrição"),
                     })


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PAGO vs ORGÂNICO
# ══════════════════════════════════════════════════════════════════════════════
with t_organic_tab:
    if df_organic.empty:
        st.warning("paid_organic_opportunity_analysis.csv não encontrado. Rode `python run_paid_organic_analysis.py`.")
    else:
        fo = to_num(df_organic.copy(),
                    ["impressions_sc", "cpa_ads", "cost_ads", "impressions_ads", "opportunity_score"])
        term_col = "search_term" if "search_term" in fo.columns else "term_key"

        def _org_strength(impr):
            if pd.isna(impr) or impr == 0: return "Fraco"
            if impr >= 500: return "Forte"
            return "Médio"

        def _paid_eff(cpa):
            if pd.isna(cpa): return "Sem dados"
            if cpa <= 20:  return "Eficiente"
            if cpa <= 40:  return "Alto CPA"
            return "Inviável"

        fo["_org"]  = fo["impressions_sc"].apply(_org_strength)
        fo["_paid"] = fo["cpa_ads"].apply(_paid_eff)

        # 4 categorias estratégicas
        MATRIX = {
            ("Forte",  "Inviável"):  ("🟢 Reduzir mídia",         "#2E7D32", "Orgânico forte: SEO pode substituir o pago"),
            ("Forte",  "Alto CPA"):  ("🟡 Melhorar ou pausar",    "#F9A825", "Orgânico sólido, mas pago ainda ineficiente"),
            ("Forte",  "Eficiente"): ("🔵 Avaliar canibalização", "#1565C0", "Ambos fortes — verificar dupla cobertura"),
            ("Médio",  "Inviável"):  ("🟡 Reforçar SEO",          "#F9A825", "Orgânico crescendo — reduzir dependência"),
            ("Médio",  "Eficiente"): ("🔵 Equilíbrio",            "#1565C0", "Estratégia balanceada"),
            ("Médio",  "Alto CPA"):  ("🟡 Otimizar pago",         "#E65100", "Melhorar lance ou ajustar anúncio"),
            ("Fraco",  "Eficiente"): ("🔴 Dependência de mídia",  "#B42828", "Sem SEO — risco se orçamento cair"),
            ("Fraco",  "Alto CPA"):  ("🔴 Repensar estratégia",   "#B42828", "Pago ineficiente, orgânico fraco"),
            ("Fraco",  "Inviável"):  ("⚫ Irrelevante",            "#9E9E9E", "Baixo volume e alto custo — considerar pausar"),
        }

        def _classify(row):
            key = (row["_org"], row["_paid"])
            return MATRIX.get(key, ("— Sem dados", "#ccc", "—"))

        fo[["Categoria", "_color", "_desc"]] = fo.apply(
            lambda r: pd.Series(_classify(r)), axis=1
        )

        # Contadores por categoria (summary row)
        cat_counts = fo["Categoria"].value_counts()
        priority_cats = ["🔴 Dependência de mídia", "🔴 Repensar estratégia",
                         "🟢 Reduzir mídia", "🔵 Avaliar canibalização"]
        summary_cats  = [c for c in priority_cats if c in cat_counts.index]

        if summary_cats:
            st.markdown("##### Distribuição estratégica")
            scols = st.columns(len(summary_cats))
            for i, cat in enumerate(summary_cats):
                _, clr, desc = MATRIX.get(
                    next((k for k, v in MATRIX.items() if v[0] == cat), ("","","")),
                    ("", "#666", "")
                )
                scols[i].markdown(
                    f"<div style='border-left:4px solid {clr};padding:6px 10px;background:#FAFAFA'>"
                    f"<div style='font-weight:700;font-size:0.82rem;color:{clr}'>{cat}</div>"
                    f"<div style='font-size:1.3rem;font-weight:700'>{cat_counts.get(cat, 0)}</div>"
                    f"<div style='font-size:0.70rem;color:#888'>{desc}</div></div>",
                    unsafe_allow_html=True,
                )
            st.divider()

        # Filtros
        f1o, f2o = st.columns(2)
        all_cats = ["Todas"] + sorted(fo["Categoria"].dropna().unique().tolist())
        sel_cat  = f1o.selectbox("Categoria estratégica", all_cats, key="o_cat")
        opts_io  = ["Todas"] + sorted(fo["intent"].dropna().unique().tolist()) if "intent" in fo.columns else ["Todas"]
        sel_io   = f2o.selectbox("Intenção", opts_io, key="o_int")

        strat = fo.copy()
        if sel_cat != "Todas": strat = strat[strat["Categoria"] == sel_cat]
        if sel_io  != "Todas" and "intent" in strat.columns:
            strat = strat[strat["intent"] == sel_io]

        st.caption(f"{len(strat)} termos")

        cols_show = [term_col, "intent", "_org", "_paid", "Categoria",
                     "impressions_sc", "cpa_ads", "opportunity_score", "recommended_action"]
        cols_ok   = [c for c in cols_show if c in strat.columns]
        st.dataframe(
            strat[cols_ok].head(150),
            use_container_width=True, hide_index=True,
            column_config={
                term_col:            st.column_config.TextColumn("Termo",      width="large"),
                "intent":            st.column_config.TextColumn("Intenção",   width="medium"),
                "_org":              st.column_config.TextColumn("Orgânico",   width="small"),
                "_paid":             st.column_config.TextColumn("Pago",       width="small"),
                "Categoria":         st.column_config.TextColumn("Categoria",  width="medium"),
                "impressions_sc":    st.column_config.NumberColumn("Impr. SC"),
                "cpa_ads":           st.column_config.NumberColumn("CPA Ads",  format="R$%.2f"),
                "opportunity_score": st.column_config.ProgressColumn("Score",  min_value=0, max_value=10),
                "recommended_action":st.column_config.TextColumn("Ação recomendada", width="medium"),
            },
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — NOVAS KEYWORDS
# ══════════════════════════════════════════════════════════════════════════════
with t_kw:
    if df_kw_new.empty:
        st.markdown("""
        <div class="empty-state">
            <h3>📭 Nenhuma sugestão disponível</h3>
            <p>Rode <code>python run_paid_organic_analysis.py</code> para gerar novas sugestões.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        fk = to_num(df_kw_new.copy(), ["impressions_sc", "position_sc", "opportunity_score"])
        if "opportunity_score" in fk.columns:
            fk = fk.sort_values("opportunity_score", ascending=False)

        # Filters
        f1k, f2k = st.columns(2)
        opts_ik = ["Todas"] + sorted(fk["intent"].dropna().unique().tolist()) if "intent" in fk.columns else ["Todas"]
        opts_pk = ["Todas"] + sorted(fk["priority"].dropna().unique().tolist()) if "priority" in fk.columns else ["Todas"]
        sel_ik = f1k.selectbox("Intenção", opts_ik, key="kw_i")
        sel_pk = f2k.selectbox("Prioridade", opts_pk, key="kw_p")
        if sel_ik != "Todas": fk = fk[fk["intent"]    == sel_ik]
        if sel_pk != "Todas": fk = fk[fk["priority"]  == sel_pk]

        n = len(fk)

        if n == 0:
            st.info("Nenhuma keyword encontrada com os filtros aplicados.")
        elif n <= 8:
            # Poucos itens: mensagem + tabela simples
            st.info(
                f"**{n} oportunidade{'s' if n != 1 else ''} nova{'s' if n != 1 else ''}** — "
                "volume baixo; foco principal deve ser otimizar keywords existentes."
            )
            tbl_cols_kw = ["keyword", "match_type", "intent", "priority",
                           "impressions_sc", "position_sc", "opportunity_score",
                           "suggested_ad_group", "reason"]
            tbl_ok_kw = [c for c in tbl_cols_kw if c in fk.columns]
            st.dataframe(fk[tbl_ok_kw], use_container_width=True, hide_index=True,
                         column_config={
                             "keyword":           st.column_config.TextColumn("Keyword",        width="large"),
                             "match_type":        st.column_config.TextColumn("Match",          width="small"),
                             "intent":            st.column_config.TextColumn("Intenção"),
                             "priority":          st.column_config.TextColumn("Prior.",          width="small"),
                             "impressions_sc":    st.column_config.NumberColumn("Impr. SC"),
                             "position_sc":       st.column_config.NumberColumn("Pos. SC",       format="%.1f"),
                             "opportunity_score": st.column_config.ProgressColumn("Score",       min_value=0, max_value=10),
                             "suggested_ad_group":st.column_config.TextColumn("Grupo Sugerido", width="large"),
                             "reason":            st.column_config.TextColumn("Motivo",          width="large"),
                         })
        else:
            # Volume relevante: cards agrupados por intenção
            st.caption(f"{n} sugestões · agrupadas por intenção")
            intent_order = ["COMPRADOR", "PESQUISADOR", "COMPARADOR", "CAÇADOR_DE_BRINDE",
                            "CONCORRENTE/MARCA_TERCEIRA", "INTENÇÃO_AMBÍGUA"]
            intents_present  = [i for i in intent_order if "intent" in fk.columns and i in fk["intent"].values]
            intents_present += [i for i in (fk["intent"].dropna().unique() if "intent" in fk.columns else [])
                                if i not in intents_present]

            for intent_group in intents_present:
                grp_df = fk[fk["intent"] == intent_group] if "intent" in fk.columns else fk
                if grp_df.empty:
                    continue
                color = INTENT_COLORS.get(intent_group, "#9E9E9E")
                st.markdown(f"**{intent_group}** · {len(grp_df)} sugestões")
                gcols = st.columns(2)
                for i, (_, row) in enumerate(grp_df.iterrows()):
                    score   = row.get("opportunity_score", 0)
                    score_v = float(score) if pd.notna(score) else 0
                    score_bar = "█" * int(score_v) + "░" * (10 - int(score_v))
                    impr    = row.get("impressions_sc", "—")
                    pos     = row.get("position_sc", "—")
                    impr_txt = f"{int(impr):,}".replace(",", ".") if pd.notna(impr) and str(impr) != "—" else "—"
                    pos_txt  = f"{float(pos):.1f}".replace(".", ",")  if pd.notna(pos)  and str(pos)  != "—" else "—"
                    with gcols[i % 2]:
                        st.markdown(f"""
                        <div class="kw-card" style="border-left-color:{color}">
                            <div class="kw-term">{row.get('keyword','—')}</div>
                            <div class="kw-meta">{row.get('match_type','')} · {str(row.get('suggested_ad_group',''))[:55]}</div>
                            <div class="kw-score">{score_bar} · {impr_txt} impr. SC · pos. {pos_txt}</div>
                            <div class="kw-score" style="margin-top:4px;color:#555">{str(row.get('reason',''))[:90]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — LANÇAMENTOS
# ══════════════════════════════════════════════════════════════════════════════
with t_launches:
    today = date.today()

    LAUNCHES = [
        {
            "produto": "Sérum Roll on Adeus Olheiras",
            "mes": "Abril 2026", "launch_date": date(2026, 4, 30), "impacto": "G",
            "keywords": [
                ["[serum roll on olheiras]",       "EXACT",  "COMPRADOR",  "Search | Exata | Adeus Olheiras"],
                ["[roll on para olheiras kokeshi]", "EXACT",  "BRANDED",    "Search Institucional bd"],
                ["[roll on olheiras]",              "EXACT",  "COMPRADOR",  "Search | Exata | Adeus Olheiras"],
                ["[serum para olheiras coreano]",   "EXACT",  "COMPRADOR",  "Search Soluções nbd"],
                ["produto coreano para olheiras",   "PHRASE", "COMPRADOR",  "Search Soluções nbd"],
                ["como tirar olheiras de vez",      "PHRASE", "PESQUISADOR","Conteúdo / Landing SEO"],
            ],
        },
        {
            "produto": "Creme Pele de Porcelana Antioleosidade",
            "mes": "Maio 2026", "launch_date": date(2026, 5, 1), "impacto": "G",
            "keywords": [
                ["[creme pele de porcelana antioleosidade]", "EXACT",  "COMPRADOR",  "Search | Exata | Antioleosidade"],
                ["[creme antioleosidade kokeshi]",           "EXACT",  "BRANDED",    "Search Institucional bd"],
                ["[hidratante antioleosidade coreano]",      "EXACT",  "COMPRADOR",  "Search Soluções nbd"],
                ["como acabar com oleosidade do rosto",      "PHRASE", "PESQUISADOR","Conteúdo / Landing SEO"],
            ],
        },
        {
            "produto": "Creme Pele de Porcelana Antissinais",
            "mes": "Maio 2026", "launch_date": date(2026, 5, 1), "impacto": "G",
            "keywords": [
                ["[creme antissinais pele de porcelana]", "EXACT",  "COMPRADOR",  "Search | Exata | Antissinais"],
                ["[creme antissinais kokeshi]",           "EXACT",  "BRANDED",    "Search Institucional bd"],
                ["[creme antienvelhecimento coreano]",    "EXACT",  "COMPRADOR",  "Search Soluções nbd"],
                ["como diminuir sinais de envelhecimento","PHRASE", "PESQUISADOR","Conteúdo / Landing SEO"],
            ],
        },
        {
            "produto": "Bastão Adeus Poros",
            "mes": "Maio 2026", "launch_date": date(2026, 5, 1), "impacto": "G",
            "keywords": [
                ["[bastão adeus poros]",               "EXACT",  "COMPRADOR",  "Search | Exata | Adeus Poros"],
                ["[bastão adeus poros kokeshi]",        "EXACT",  "BRANDED",    "Search Institucional bd"],
                ["[bastão para poros abertos]",         "EXACT",  "COMPRADOR",  "Search | Exata | Adeus Poros"],
                ["produto coreano para poros abertos",  "PHRASE", "COMPRADOR",  "Search Soluções nbd"],
                ["como fechar os poros do rosto",       "PHRASE", "PESQUISADOR","Conteúdo / Landing SEO"],
            ],
        },
        {
            "produto": "Dia das Mães",
            "mes": "Maio 2026", "launch_date": date(2026, 5, 11), "impacto": "M",
            "keywords": [
                ["[kit presente dia das mães kokeshi]", "EXACT",  "COMPRADOR","Search Sazonais Dia das Mães"],
                ["[presente skincare dia das mães]",    "EXACT",  "COMPRADOR","Search Sazonais Dia das Mães"],
                ["kit skincare dia das mães",           "PHRASE", "COMPRADOR","Search Sazonais Dia das Mães"],
            ],
        },
        {
            "produto": "Bastão Adeus Linhas",
            "mes": "Junho 2026", "launch_date": date(2026, 6, 1), "impacto": "G",
            "keywords": [
                ["[bastão adeus linhas]",              "EXACT",  "COMPRADOR",  "Search | Exata | Adeus Linhas"],
                ["[bastão para linhas de expressão]",  "EXACT",  "COMPRADOR",  "Search | Exata | Adeus Linhas"],
                ["como diminuir linhas de expressão",  "PHRASE", "PESQUISADOR","Conteúdo / Landing SEO"],
            ],
        },
        {
            "produto": "Creme Pele de Porcelana FPS 20",
            "mes": "Junho 2026", "launch_date": date(2026, 6, 1), "impacto": "G",
            "keywords": [
                ["[creme fps 20 kokeshi]",             "EXACT",  "BRANDED",  "Search Institucional bd"],
                ["[hidratante com fps coreano]",        "EXACT",  "COMPRADOR","Search Soluções nbd"],
                ["[creme com protetor solar fps 20]",   "EXACT",  "COMPRADOR","Search | Exata | FPS"],
                ["hidratante e protetor solar em um só","PHRASE", "COMPRADOR","Search Soluções nbd"],
            ],
        },
        {
            "produto": "Black November + Black Friday",
            "mes": "Novembro 2026", "launch_date": date(2026, 11, 1), "impacto": "G",
            "keywords": [
                ["[kokeshi black friday]",          "EXACT",  "BRANDED",  "Search Institucional bd"],
                ["[black friday skincare]",         "EXACT",  "COMPRADOR","Search Sazonais BF"],
                ["[kit skincare black friday]",     "EXACT",  "COMPRADOR","Search Sazonais BF"],
                ["desconto black friday skincare",  "PHRASE", "CAÇADOR",  "Monitorar — negativar se CPA alto"],
            ],
        },
    ]

    st.subheader("📅 Calendário de Lançamentos 2026")

    for launch in LAUNCHES:
        days_to = (launch["launch_date"] - today).days
        countdown = f"em {days_to} dias" if days_to > 0 else "HOJE" if days_to == 0 else f"há {abs(days_to)} dias"
        status    = "🔴 URGENTE" if days_to <= 7 else "🟠 IMINENTE" if days_to <= 30 else "🟡 PREPARAR" if days_to <= 60 else "🟢 PLANEJAMENTO"
        imp_badge = f"**[G]** — Campanha dedicada" if launch["impacto"] == "G" else "**[M]** — Adicionar ao grupo existente"

        with st.expander(f"{status}  {launch['produto']} — {launch['mes']} ({countdown})",
                         expanded=(days_to <= 30)):
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.markdown(f"**Produto:** {launch['produto']}")
            c2.markdown(f"**Impacto:** {imp_badge}")
            c3.markdown(f"`{countdown}`")

            df_kl = pd.DataFrame(launch["keywords"], columns=["Keyword", "Match", "Intenção", "Grupo Sugerido"])
            st.dataframe(df_kl, use_container_width=True, hide_index=True)

            if launch["impacto"] == "G" and 0 < days_to <= 45:
                st.info("**Impacto G — ação necessária agora:** criar campanha/grupo dedicado + adicionar ao feed Shopping.")
            elif launch["impacto"] == "M" and 0 < days_to <= 15:
                st.info("**Impacto M — ação necessária agora:** adicionar keywords ao grupo existente mais relevante.")
