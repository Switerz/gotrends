import pandas as pd

from tools.google_ads_reader import (
    get_campaigns_last_7_days,
    get_ad_groups_last_7_days,
    get_keywords_last_7_days,
    get_search_terms_last_7_days,
)

TICKET_MEDIO = 90.0


def classify_campaign(campaign_name: str) -> str:
    name = str(campaign_name).lower()

    if "institucional" in name or "brand" in name or "branded" in name or "| bd" in name:
        return "BRANDED"

    if "nbd" in name or "non" in name or "soluções" in name:
        return "NON_BRANDED"

    return "OTHER"


def safe_div(a, b):
    if b in [0, None] or pd.isna(b):
        return None
    return a / b


def add_business_context(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["campaign_type"] = df["campaign_name"].apply(classify_campaign)

    df["target_roas"] = df["campaign_type"].map({
        "BRANDED": 25.0,
        "NON_BRANDED": 2.4,
        "OTHER": None,
    })

    return df


def analyze_terms(df_terms: pd.DataFrame) -> pd.DataFrame:
    if df_terms.empty:
        return pd.DataFrame()

    df = add_business_context(df_terms)
    df["search_intent"] = df["search_term"].apply(classify_search_intent)
    df["product_focus"] = df["search_term"].apply(classify_product_focus)

    # =====================================================
    # MÉTRICAS FINANCEIRAS
    # =====================================================
    converting = df[df["conversions"].fillna(0) > 0]
    if not converting.empty:
        account_cpa_ref = converting["cost"].sum() / converting["conversions"].sum()
    else:
        account_cpa_ref = 11.92

    df["revenue_estimate"] = (df["conversions"].fillna(0) * TICKET_MEDIO).round(2)
    df["roas_estimate"] = df.apply(
        lambda r: round(r["revenue_estimate"] / r["cost"], 2) if r["cost"] > 0 else None,
        axis=1,
    )
    df["potential_revenue_same_spend"] = ((df["cost"] / account_cpa_ref) * TICKET_MEDIO).round(2)
    df["opportunity_revenue_delta"] = df.apply(
        lambda r: round(r["potential_revenue_same_spend"] - r["revenue_estimate"], 2)
        if (pd.notna(r["cpa"]) and r["cpa"] > 40)
        else None,
        axis=1,
    )

    df["action"] = "MANTER"
    df["priority"] = "BAIXA"
    df["reason"] = "Sem alerta relevante"

    # ... suas regras atuais de NON-BRANDED e BRANDED ...

    # =====================================================
    # REGRAS INTELIGENTES POR INTENÇÃO DE BUSCA
    # =====================================================

    mask_freebie = (
        (df["campaign_type"] == "NON_BRANDED")
        & (df["search_intent"] == "CAÇADOR_DE_BRINDE")
        & (df["cost"] >= 5)
        & (df["conversions"].fillna(0) == 0)
    )

    df.loc[mask_freebie, "action"] = "SUGERIR_NEGATIVA"
    df.loc[mask_freebie, "priority"] = "ALTA"
    df.loc[mask_freebie, "reason"] = (
        "Termo com intenção de brinde/desconto e sem conversão"
    )

    mask_competitor_no_conv = (
        (df["campaign_type"] == "NON_BRANDED")
        & (df["search_intent"] == "CONCORRENTE/MARCA_TERCEIRA")
        & (df["cost"] >= 10)
        & (df["conversions"].fillna(0) == 0)
    )

    df.loc[mask_competitor_no_conv, "action"] = "REVISAR_OU_NEGATIVAR"
    df.loc[mask_competitor_no_conv, "priority"] = "MEDIA"
    df.loc[mask_competitor_no_conv, "reason"] = (
        "Termo de concorrente/marca terceira sem conversão"
    )

    mask_buyer_good = (
        (df["campaign_type"] == "NON_BRANDED")
        & (df["search_intent"] == "COMPRADOR")
        & (df["conversions"].fillna(0) > 0)
        & (df["cpa"].notna())
        & (df["cpa"] <= 25)
    )

    df.loc[mask_buyer_good, "action"] = "CRIAR_KEYWORD_EXATA"
    df.loc[mask_buyer_good, "priority"] = "ALTA"
    df.loc[mask_buyer_good, "reason"] = (
        "Termo comprador com conversão e CPA saudável"
    )

    mask_researcher_good = (
        (df["campaign_type"] == "NON_BRANDED")
        & (df["search_intent"] == "PESQUISADOR")
        & (df["conversions"].fillna(0) > 0)
        & (df["cpa"].notna())
        & (df["cpa"] <= 20)
    )

    df.loc[mask_researcher_good, "action"] = "CRIAR_CONTEUDO_OU_LANDING"
    df.loc[mask_researcher_good, "priority"] = "MEDIA"
    df.loc[mask_researcher_good, "reason"] = (
        "Termo informacional converte; pode virar conteúdo, landing ou grupo específico"
    )

    # =====================================================
    # REGRAS BASEADAS EM ECONOMIA REAL
    # =====================================================

    mask_cpa_critical = (
        df["cpa"].notna()
        & (df["cpa"] >= 50)
    )

    df.loc[mask_cpa_critical, "action"] = "CORTAR_OU_NEGATIVAR"
    df.loc[mask_cpa_critical, "priority"] = "ALTA"
    df.loc[mask_cpa_critical, "reason"] = "CPA acima de R$50 (inviável economicamente)"

    mask_cpa_high = (
        df["cpa"].notna()
        & (df["cpa"] >= 40)
        & (df["cpa"] < 50)
    )

    df.loc[mask_cpa_high, "action"] = "REVISAR_URGENTE"
    df.loc[mask_cpa_high, "priority"] = "ALTA"
    df.loc[mask_cpa_high, "reason"] = "CPA acima de R$40 (acima do limite saudável)"

    mask_cpa_good = (
        df["cpa"].notna()
        & (df["cpa"] <= 20)
        & (df["conversions"].fillna(0) > 0)
    )

    df.loc[mask_cpa_good, "action"] = "ESCALAR"
    df.loc[mask_cpa_good, "priority"] = "ALTA"
    df.loc[mask_cpa_good, "reason"] = "CPA abaixo de R$20 (excelente performance)"

    mask_flagship = (
        df["product_focus"].isin([
            "OLHOS_DE_GUEIXA",
            "PELE_DE_PORCELANA",
            "CREME_FACIAL",
            "KIT_SKINCARE",
        ])
        & (df["cpa"].notna())
        & (df["cpa"] <= 25)
        & (df["conversions"].fillna(0) > 0)
    )

    df.loc[mask_flagship, "priority"] = "ALTA"
    df.loc[mask_flagship, "reason"] = (
        df.loc[mask_flagship, "reason"].astype(str)
        + " | Produto/categoria prioritária com boa performance"
    )

    priority_order = {
        "ALTA": 1,
        "MEDIA": 2,
        "BAIXA": 3,
    }

    df["priority_rank"] = df["priority"].map(priority_order).fillna(99)

    return df.sort_values(
        ["priority_rank", "cost"],
        ascending=[True, False]
    )


def summarize_account(df_campaigns, df_adgroups, df_keywords, df_terms_analysis):
    total_cost = df_campaigns["cost"].sum() if not df_campaigns.empty else 0
    total_conversions = df_campaigns["conversions"].sum() if not df_campaigns.empty else 0
    account_cpa = safe_div(total_cost, total_conversions)

    high_priority = df_terms_analysis[df_terms_analysis["priority"] == "ALTA"] if not df_terms_analysis.empty else pd.DataFrame()
    negatives = df_terms_analysis[df_terms_analysis["action"] == "SUGERIR_NEGATIVA"] if not df_terms_analysis.empty else pd.DataFrame()
    exacts = df_terms_analysis[df_terms_analysis["action"] == "CRIAR_KEYWORD_EXATA"] if not df_terms_analysis.empty else pd.DataFrame()

    # Métricas financeiras
    total_revenue_estimate = round(float(total_conversions) * TICKET_MEDIO, 2) if total_conversions else 0
    account_roas = round(total_revenue_estimate / float(total_cost), 2) if total_cost > 0 else None

    if not df_terms_analysis.empty and account_cpa:
        bad_terms = df_terms_analysis[df_terms_analysis["cpa"].notna() & (df_terms_analysis["cpa"] > 40)]
        inviable_terms = df_terms_analysis[df_terms_analysis["cpa"].notna() & (df_terms_analysis["cpa"] > 50)]

        wasted_spend_cpa40 = round(float(bad_terms["cost"].sum()), 2)
        wasted_spend_cpa50 = round(float(inviable_terms["cost"].sum()), 2)

        potential_conv_from_waste = bad_terms["cost"].sum() / account_cpa
        actual_conv_from_waste = bad_terms["conversions"].fillna(0).sum()
        opportunity_revenue_lost = round(
            float((potential_conv_from_waste - actual_conv_from_waste) * TICKET_MEDIO), 2
        )

        # Cenários de forecast (30 dias)
        forecast_conservative = round(float((wasted_spend_cpa50 * 0.5) / account_cpa * TICKET_MEDIO), 2)
        forecast_base = round(float((wasted_spend_cpa40 * 0.75) / account_cpa * TICKET_MEDIO), 2)
        forecast_optimistic = round(float((wasted_spend_cpa40 * 1.0) / account_cpa * TICKET_MEDIO), 2)

        scale_candidates = df_terms_analysis[
            df_terms_analysis["cpa"].notna()
            & (df_terms_analysis["cpa"] <= 15)
            & (df_terms_analysis["conversions"].fillna(0) >= 2)
        ]
        scale_revenue_upside_50pct = round(
            float(scale_candidates["cost"].sum() * 0.5 / account_cpa * TICKET_MEDIO), 2
        ) if not scale_candidates.empty else 0
    else:
        wasted_spend_cpa40 = 0
        wasted_spend_cpa50 = 0
        opportunity_revenue_lost = None
        forecast_conservative = None
        forecast_base = None
        forecast_optimistic = None
        scale_revenue_upside_50pct = 0

    summary = {
        "total_cost": round(float(total_cost), 2),
        "total_conversions": round(float(total_conversions), 2),
        "account_cpa": round(float(account_cpa), 2) if account_cpa else None,
        "total_revenue_estimate": total_revenue_estimate,
        "account_roas": account_roas,
        "wasted_spend_cpa40plus": wasted_spend_cpa40,
        "wasted_spend_cpa50plus": wasted_spend_cpa50,
        "opportunity_revenue_lost_30d": opportunity_revenue_lost,
        "scale_revenue_upside_50pct_winners": scale_revenue_upside_50pct,
        "forecast_revenue_gain_conservative": forecast_conservative,
        "forecast_revenue_gain_base": forecast_base,
        "forecast_revenue_gain_optimistic": forecast_optimistic,
        "campaigns_count": int(len(df_campaigns)),
        "adgroups_count": int(len(df_adgroups)),
        "keywords_count": int(len(df_keywords)),
        "search_terms_count": int(len(df_terms_analysis)),
        "high_priority_count": int(len(high_priority)),
        "suggested_negatives_count": int(len(negatives)),
        "suggested_exact_keywords_count": int(len(exacts)),
    }

    return summary


def run_google_ads_growth_analysis():
    df_campaigns = get_campaigns_last_7_days()
    df_adgroups = get_ad_groups_last_7_days()
    df_keywords = get_keywords_last_7_days()
    df_terms = get_search_terms_last_7_days()

    df_campaigns = add_business_context(df_campaigns)
    df_adgroups = add_business_context(df_adgroups)
    df_keywords = add_business_context(df_keywords)
    df_terms_analysis = analyze_terms(df_terms)

    summary = summarize_account(
        df_campaigns,
        df_adgroups,
        df_keywords,
        df_terms_analysis,
    )

    top_actions = (
        df_terms_analysis[
            df_terms_analysis["action"] != "MANTER"
        ][
            [
                "campaign_name",
                "ad_group_name",
                "search_term",
                "search_intent",
                "product_focus",
                "campaign_type",
                "cost",
                "clicks",
                "conversions",
                "ctr",
                "avg_cpc",
                "cpa",
                "revenue_estimate",
                "roas_estimate",
                "opportunity_revenue_delta",
                "action",
                "priority",
                "reason",
            ]
        ]
        .head(30)
        .to_dict(orient="records")
        if not df_terms_analysis.empty
        else []
    )

    return {
        "summary": summary,
        "top_actions": top_actions,
    }

def classify_search_intent(term: str) -> str:
    term = str(term).lower()

    brinde_words = [
        "brinde", "gratis", "grátis", "amostra grátis", "cupom",
        "desconto", "promoção", "promocao"
    ]

    preco_words = [
        "preço", "preco", "valor", "barato", "mais barato",
        "onde comprar", "comprar", "loja", "site oficial"
    ]

    comparador_words = [
        "melhor", "vs", "versus", "comparação", "comparacao",
        "resenha", "review", "vale a pena", "opinião", "opiniao"
    ]

    pesquisador_words = [
        "como", "o que é", "o que e", "para que serve",
        "benefícios", "beneficios", "rotina", "pele oleosa",
        "pele seca", "manchas", "poros", "colágeno", "colageno"
    ]

    concorrente_words = [
        "principia", "anua", "beauty of joseon", "medicube",
        "axis y", "kikoshi", "creamy"
    ]

    if any(w in term for w in brinde_words):
        return "CAÇADOR_DE_BRINDE"

    if any(w in term for w in concorrente_words):
        return "CONCORRENTE/MARCA_TERCEIRA"

    if any(w in term for w in preco_words):
        return "COMPRADOR"

    if any(w in term for w in comparador_words):
        return "COMPARADOR"

    if any(w in term for w in pesquisador_words):
        return "PESQUISADOR"

    return "INTENÇÃO_AMBÍGUA"

def classify_product_focus(term: str) -> str:
    term = str(term).lower()

    if "gueixa" in term:
        return "OLHOS_DE_GUEIXA"

    # sérum roll on / adeus olheiras (lançamento abr/26)
    if "roll on" in term or "adeus olheiras" in term or ("serum" in term and "olheira" in term):
        return "ADEUS_OLHEIRAS"

    # bastões (lançamentos mai/jun 26)
    if "adeus poros" in term or ("bastão" in term and "poros" in term) or ("bastao" in term and "poros" in term):
        return "BASTAO_ADEUS_POROS"

    if "adeus linhas" in term or ("bastão" in term and "linha" in term) or ("bastao" in term and "linha" in term):
        return "BASTAO_ADEUS_LINHAS"

    # sérum de arroz (lançamento mar/26)
    if "serum de arroz" in term or "sérum de arroz" in term or ("serum" in term and "arroz" in term):
        return "SERUM_ARROZ"

    if "porcelana" in term:
        return "PELE_DE_PORCELANA"

    if "creme" in term or "hidratante facial" in term:
        return "CREME_FACIAL"

    if "kit" in term:
        return "KIT_SKINCARE"

    if "skincare" in term or "skin care" in term:
        return "SKINCARE"

    return "OUTROS"