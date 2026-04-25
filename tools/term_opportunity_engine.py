"""
Engine v5: Google Ads + Search Console

Novidades vs v4:
- usa search_budget_lost_impression_share quando existir no CSV de Ads;
- sugere novas keywords vindas do Search Console;
- gera new_keyword_suggestions.csv;
- mantém decisão consolidada + breakdown granular.
"""

import re
import pandas as pd
import numpy as np

TICKET_MEDIO = 90.0
PRIORITY_ORDER = {"alta": 0, "média": 1, "media": 1, "baixa": 2}

BRAND_PATTERNS = ["kokeshi", "kokesi", "kokesh", "kokechi"]
PRIORITY_PRODUCT_PATTERNS = [
    "pele de porcelana", "olhos de gueixa", "olho de gueixa",
    "gota de colageno", "gota de colágeno", "creme facial",
    "creme coreano", "skincare coreano", "hidratante coreano",
    "body splash", "cheiro de rica",
    # lançamentos 2026
    "serum de arroz", "sérum de arroz", "serum arroz",
    "adeus olheiras", "roll on olheiras", "roll on para olheiras",
    "serum roll on", "sérum roll on",
    "antioleosidade", "antissinais", "pele sensível kokeshi",
    "bastão adeus poros", "bastao adeus poros", "adeus poros",
    "bastão adeus linhas", "bastao adeus linhas", "adeus linhas",
    "fps 20 kokeshi", "creme fps",
]
BUYER_PATTERNS = [
    "comprar", "preço", "preco", "valor", "kit", "produto", "loja",
    "original", "oficial", "hidratante", "creme", "serum", "sérum",
    "skincare", "body splash", "colageno", "colágeno",
]
INFORMATIONAL_PATTERNS = [
    "como", "o que é", "o que e", "para que serve", "benefícios",
    "beneficios", "resenha", "vale a pena", "antes e depois",
]
NOISE_PATTERNS = ["site:", "-site:", " inurl:", " intitle:", " filetype:", "http://", "https://", "www."]
EXACT_NOISE_TERMS = {"kokichi", "kokichi ouma", "kokushi", "product"}
COMPETITOR_OR_THIRD_PARTY_PATTERNS = [
    "principia", "anua", "beauty of joseon", "medicube", "axis y",
    "beleza na web", "clarins", "elroel", "kikoshi", "creamy",
]


def normalize_term(value: str) -> str:
    if pd.isna(value):
        return ""
    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def contains_any(term: str, patterns: list[str]) -> bool:
    return any(pattern in term for pattern in patterns)


def is_brand(term: str) -> bool:
    return contains_any(term, BRAND_PATTERNS)


def is_priority_product(term: str) -> bool:
    return contains_any(term, PRIORITY_PRODUCT_PATTERNS)


def is_competitor_or_third_party(term: str) -> bool:
    return contains_any(term, COMPETITOR_OR_THIRD_PARTY_PATTERNS)


def is_coupon_or_freebie(term: str) -> bool:
    return any(x in term for x in ["cupom", "desconto", "promo", "gratis", "grátis", "brinde", "amostra"])


def classify_intent(term: str) -> str:
    if is_brand(term):
        return "BRANDED"
    if is_coupon_or_freebie(term):
        return "CAÇADOR_DE_BRINDE"
    if is_competitor_or_third_party(term):
        return "CONCORRENTE/MARCA_TERCEIRA"
    if contains_any(term, BUYER_PATTERNS) or is_priority_product(term):
        return "COMPRADOR"
    if contains_any(term, INFORMATIONAL_PATTERNS):
        return "PESQUISADOR/COMPARADOR"
    return "AMBÍGUA"


def is_noise_query(term: str) -> bool:
    if not term or term in EXACT_NOISE_TERMS:
        return True
    if contains_any(term, NOISE_PATTERNS):
        return True
    if sum(ch.isdigit() for ch in term) >= 8:
        return True
    if len(term.split()) > 8 and not is_brand(term) and not is_priority_product(term):
        return True
    if len(term) > 120:
        return True
    return False


def safe_float(value, default=0.0):
    if value is None or pd.isna(value) or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def expected_ctr_by_position(position: float) -> float:
    if position <= 1.5: return 0.18
    if position <= 3: return 0.10
    if position <= 5: return 0.05
    if position <= 10: return 0.02
    return 0.01


def normalize_lost_is(value):
    # Google Ads retorna fração: 0.35 = 35%; 0.9001 = >90%.
    return max(safe_float(value, 0), 0)


def _apply_campaign_is(ads: pd.DataFrame, campaign_is: "pd.DataFrame | None") -> pd.DataFrame:
    """Drops term-level IS (always 0 from search_term_view) and joins campaign-level IS by campaign_name."""
    for col in ["search_budget_lost_impression_share", "search_rank_lost_impression_share"]:
        if col in ads.columns:
            ads = ads.drop(columns=[col])
    if campaign_is is not None and "campaign_name" in ads.columns and not campaign_is.empty:
        is_cols = [c for c in ["campaign_name", "search_budget_lost_impression_share", "search_rank_lost_impression_share"] if c in campaign_is.columns]
        ads = ads.merge(campaign_is[is_cols].drop_duplicates("campaign_name"), on="campaign_name", how="left")
    for col in ["search_budget_lost_impression_share", "search_rank_lost_impression_share"]:
        if col not in ads.columns:
            ads[col] = 0
        ads[col] = pd.to_numeric(ads[col], errors="coerce").fillna(0).apply(normalize_lost_is)
    return ads


def prepare_ads_terms(ads: pd.DataFrame, campaign_is: "pd.DataFrame | None" = None, ads_term_col: str = "search_term") -> pd.DataFrame:
    ads = ads.copy()
    ads["term_key"] = ads[ads_term_col].apply(normalize_term)
    ads = ads[ads["term_key"] != ""].copy()

    for col in ["impressions", "clicks", "cost", "conversions"]:
        if col not in ads.columns:
            ads[col] = 0
        ads[col] = pd.to_numeric(ads[col], errors="coerce").fillna(0)

    ads = _apply_campaign_is(ads, campaign_is)

    group = ads.groupby("term_key", as_index=False).agg(
        search_term=("term_key", "first"),
        ads_campaigns=("campaign_name", lambda x: " | ".join(sorted(set(map(str, x.dropna())))[:4])) if "campaign_name" in ads.columns else ("term_key", "first"),
        ads_ad_groups=("ad_group_name", lambda x: " | ".join(sorted(set(map(str, x.dropna())))[:4])) if "ad_group_name" in ads.columns else ("term_key", "first"),
        impressions_ads=("impressions", "sum"),
        clicks_ads=("clicks", "sum"),
        cost_ads=("cost", "sum"),
        conversions_ads=("conversions", "sum"),
        search_budget_lost_impression_share=("search_budget_lost_impression_share", "max"),
    )
    group["ctr_ads"] = np.where(group["impressions_ads"] > 0, group["clicks_ads"] / group["impressions_ads"], 0)
    group["avg_cpc_ads"] = np.where(group["clicks_ads"] > 0, group["cost_ads"] / group["clicks_ads"], np.nan)
    group["cpa_ads"] = np.where(group["conversions_ads"] > 0, group["cost_ads"] / group["conversions_ads"], np.nan)
    return group


def prepare_ads_breakdown(ads: pd.DataFrame, campaign_is: "pd.DataFrame | None" = None, ads_term_col: str = "search_term") -> pd.DataFrame:
    ads = ads.copy()
    ads["term_key"] = ads[ads_term_col].apply(normalize_term)
    ads = ads[ads["term_key"] != ""].copy()

    for col in ["impressions", "clicks", "cost", "conversions"]:
        if col not in ads.columns:
            ads[col] = 0
        ads[col] = pd.to_numeric(ads[col], errors="coerce").fillna(0)

    ads = _apply_campaign_is(ads, campaign_is)

    if "campaign_name" not in ads.columns: ads["campaign_name"] = "unknown_campaign"
    if "ad_group_name" not in ads.columns: ads["ad_group_name"] = "unknown_ad_group"

    breakdown = ads.groupby(["term_key", "campaign_name", "ad_group_name"], as_index=False).agg(
        impressions_ads_detail=("impressions", "sum"),
        clicks_ads_detail=("clicks", "sum"),
        cost_ads_detail=("cost", "sum"),
        conversions_ads_detail=("conversions", "sum"),
        search_budget_lost_impression_share_detail=("search_budget_lost_impression_share", "max"),
    )
    breakdown["ctr_ads_detail"] = np.where(breakdown["impressions_ads_detail"] > 0, breakdown["clicks_ads_detail"] / breakdown["impressions_ads_detail"], 0)
    breakdown["avg_cpc_ads_detail"] = np.where(breakdown["clicks_ads_detail"] > 0, breakdown["cost_ads_detail"] / breakdown["clicks_ads_detail"], np.nan)
    breakdown["cpa_ads_detail"] = np.where(breakdown["conversions_ads_detail"] > 0, breakdown["cost_ads_detail"] / breakdown["conversions_ads_detail"], np.nan)
    breakdown["detail_recommendation"] = breakdown.apply(classify_ads_detail_row, axis=1)
    return breakdown


def classify_ads_detail_row(row: pd.Series) -> str:
    cost = safe_float(row.get("cost_ads_detail"), 0)
    conversions = safe_float(row.get("conversions_ads_detail"), 0)
    clicks = safe_float(row.get("clicks_ads_detail"), 0)
    cpa = safe_float(row.get("cpa_ads_detail"), np.nan)
    lost_is = safe_float(row.get("search_budget_lost_impression_share_detail"), 0)
    if conversions >= 2 and (pd.isna(cpa) or cpa <= 30) and lost_is >= 0.20:
        return "escalar_budget_neste_grupo"
    if conversions >= 2 and (pd.isna(cpa) or cpa <= 30):
        return "manter_escalar_neste_grupo"
    if conversions > 0 and (pd.isna(cpa) or cpa <= 40):
        return "manter_otimizar_neste_grupo"
    if cost >= 50 and conversions == 0:
        return "revisar_ou_reduzir_neste_grupo"
    if cost >= 30 and conversions == 0:
        return "monitorar_com_risco_neste_grupo"
    if clicks >= 20 and conversions == 0:
        return "revisar_intencao_neste_grupo"
    return "monitorar"


def prepare_search_console_terms(sc: pd.DataFrame, sc_term_col: str = "query", min_sc_impressions: int = 10) -> pd.DataFrame:
    sc = sc.copy()
    sc["term_key"] = sc[sc_term_col].apply(normalize_term)
    sc = sc[sc["term_key"] != ""].copy()
    sc = sc[~sc["term_key"].apply(is_noise_query)].copy()
    for col in ["clicks", "impressions", "ctr", "position"]:
        if col not in sc.columns:
            sc[col] = 0
        sc[col] = pd.to_numeric(sc[col], errors="coerce").fillna(0)
    sc = sc[sc["impressions"] >= min_sc_impressions].copy()
    sc["_weighted_position"] = sc["position"] * sc["impressions"]
    group = sc.groupby("term_key", as_index=False).agg(
        query_sc=("term_key", "first"),
        clicks_sc=("clicks", "sum"),
        impressions_sc=("impressions", "sum"),
        weighted_position_sum=("_weighted_position", "sum"),
    )
    group["ctr_sc"] = np.where(group["impressions_sc"] > 0, group["clicks_sc"] / group["impressions_sc"], 0)
    group["position_sc"] = np.where(group["impressions_sc"] > 0, group["weighted_position_sum"] / group["impressions_sc"], np.nan)
    return group.drop(columns=["weighted_position_sum"])


def classify_paid_organic_opportunity(row: pd.Series) -> dict:
    term = normalize_term(row.get("term_key", ""))
    intent = classify_intent(term)
    ads_cost = safe_float(row.get("cost_ads"), 0)
    ads_conversions = safe_float(row.get("conversions_ads"), 0)
    ads_clicks = safe_float(row.get("clicks_ads"), 0)
    ads_impressions = safe_float(row.get("impressions_ads"), 0)
    cpa_ads = safe_float(row.get("cpa_ads"), np.nan)
    lost_is = safe_float(row.get("search_budget_lost_impression_share"), 0)
    organic_impressions = safe_float(row.get("impressions_sc"), 0)
    organic_ctr = safe_float(row.get("ctr_sc"), 0)
    organic_position = safe_float(row.get("position_sc"), 99)

    has_ads = ads_impressions > 0 or ads_clicks > 0 or ads_cost > 0 or ads_conversions > 0
    has_sc = organic_impressions > 0
    branded = is_brand(term)
    priority_product = is_priority_product(term)
    competitor = is_competitor_or_third_party(term)
    coupon = is_coupon_or_freebie(term)
    expected_ctr = expected_ctr_by_position(organic_position)

    score = 0
    reasons = []
    action = "monitorar"
    priority = "baixa"

    if organic_impressions >= 100: score += 1; reasons.append("demanda orgânica relevante")
    if organic_impressions >= 500: score += 2; reasons.append("alta impressão orgânica")
    if organic_impressions >= 1000: score += 2; reasons.append("demanda orgânica muito forte")
    if has_sc and organic_position > 5 and organic_impressions >= 100: score += 2; reasons.append("posição orgânica com espaço para captura")
    if has_sc and organic_ctr < expected_ctr * 0.5 and organic_impressions >= 100: score += 1; reasons.append("CTR orgânico abaixo do esperado")
    if ads_clicks >= 20: score += 1; reasons.append("volume pago relevante")
    if ads_clicks >= 50: score += 1; reasons.append("alto volume de cliques pagos")
    if ads_conversions > 0: score += 3; reasons.append("termo já converte no Google Ads")
    if ads_conversions >= 3: score += 3; reasons.append("múltiplas conversões no Google Ads")
    if not np.isnan(cpa_ads):
        if cpa_ads <= 20: score += 3; reasons.append("CPA ótimo")
        elif cpa_ads <= 30: score += 2; reasons.append("CPA aceitável")
        elif cpa_ads > 50: score -= 2; reasons.append("CPA crítico")
    if lost_is >= 0.20 and ads_conversions > 0 and (np.isnan(cpa_ads) or cpa_ads <= 40):
        score += 2; reasons.append("perda de impressão por orçamento em termo que converte")
    if lost_is >= 0.40 and ads_conversions > 0 and (np.isnan(cpa_ads) or cpa_ads <= 30):
        score += 3; reasons.append("alta restrição de orçamento em termo eficiente")
    if priority_product: score += 2; reasons.append("produto/categoria prioritária")
    if coupon: score -= 1; reasons.append("termo de cupom/desconto exige cautela de margem")
    if competitor: score -= 1; reasons.append("termo de concorrente/marca terceira")
    if ads_cost >= 30 and ads_conversions == 0: score -= 3; reasons.append("custo pago relevante sem conversão")
    if ads_cost >= 100 and ads_conversions == 0: score -= 4; reasons.append("desperdício pago alto sem conversão")

    is_buyer_intent = intent in ("COMPRADOR", "PESQUISADOR/COMPARADOR") or priority_product
    if not has_ads and not branded and not coupon and (
        (organic_impressions >= 100 and is_buyer_intent) or organic_impressions >= 300
    ):
        action = "sugerir_nova_keyword_exata"
        priority = "alta" if is_buyer_intent else "média"
        score += 3
        reasons.append("query orgânica com demanda e baixa cobertura paga")
    elif branded:
        action = "proteger_branded_e_monitorar_incrementalidade"
        priority = "alta" if ads_conversions > 0 or organic_impressions >= 500 else "média"
    elif ads_conversions >= 2 and (np.isnan(cpa_ads) or cpa_ads <= 30) and lost_is >= 0.30:
        action = "escalar_budget_com_controle"; priority = "alta"
    elif ads_cost >= 30 and ads_conversions == 0 and (organic_impressions < 100 or competitor or coupon):
        action = "revisar_ou_negativar_com_cautela"; priority = "alta" if ads_cost >= 50 else "média"
    elif ads_conversions >= 2 and (np.isnan(cpa_ads) or cpa_ads <= 30) and organic_impressions >= 100 and organic_position > 5:
        action = "escalar_pago_e_otimizar_seo"; priority = "alta"
    elif ads_conversions >= 2 and (np.isnan(cpa_ads) or cpa_ads <= 30):
        action = "escalar_pago_com_controle"; priority = "alta"
    elif ads_conversions > 0 and (np.isnan(cpa_ads) or cpa_ads <= 40):
        action = "manter_e_otimizar"; priority = "média"
    elif not has_ads and organic_impressions >= 500 and organic_position > 5:
        action = "testar_google_ads_e_otimizar_seo"; priority = "média"
    elif has_ads and organic_impressions >= 500 and organic_position > 5 and ads_conversions == 0:
        action = "revisar_intencao_copy_e_landing"; priority = "média"
    elif has_sc and organic_impressions >= 200 and organic_ctr < expected_ctr * 0.5:
        action = "otimizar_seo_snippet_e_landing"; priority = "média"
    elif has_ads and organic_position <= 2 and organic_ctr >= 0.10 and ads_conversions == 0 and ads_cost > 0:
        action = "avaliar_economia_de_midia"; priority = "média"
    elif ads_conversions > 0 and not has_sc:
        action = "manter_ads_monitorar_seo"; priority = "média"

    return {
        "source_match": "ads+search_console" if has_ads and has_sc else ("ads_only" if has_ads else "search_console_only"),
        "intent": intent,
        "is_branded": branded,
        "is_priority_product": priority_product,
        "is_competitor_or_third_party": competitor,
        "is_coupon_or_freebie": coupon,
        "expected_ctr_sc": round(expected_ctr, 4),
        "opportunity_score": int(score),
        "recommended_action": action,
        "priority": priority,
        "reason": "; ".join(dict.fromkeys(reasons)) if reasons else "sem sinal forte",
    }


def summarize_breakdown_for_term(term_key: str, breakdown: pd.DataFrame, max_rows: int = 5) -> str:
    rows = breakdown[breakdown["term_key"] == term_key].copy()
    if rows.empty: return ""
    rows = rows.sort_values(by=["conversions_ads_detail", "cost_ads_detail"], ascending=[False, False]).head(max_rows)
    parts = []
    for _, row in rows.iterrows():
        cpa = row["cpa_ads_detail"]
        cpa_text = "sem CPA" if pd.isna(cpa) else f"CPA R${cpa:.2f}"
        lost = safe_float(row.get("search_budget_lost_impression_share_detail"), 0)
        parts.append(f'{row["campaign_name"]} / {row["ad_group_name"]}: custo R${row["cost_ads_detail"]:.2f}, conv {row["conversions_ads_detail"]:.1f}, {cpa_text}, perda orçamento {lost:.0%}, {row["detail_recommendation"]}')
    return " || ".join(parts)


def generate_new_keyword_suggestions(result: pd.DataFrame, output_path: str = "new_keyword_suggestions.csv") -> pd.DataFrame:
    df = result[result["recommended_action"].isin(["sugerir_nova_keyword_exata", "testar_google_ads_e_otimizar_seo"])].copy()
    if df.empty:
        empty = pd.DataFrame(columns=["keyword", "match_type", "suggested_ad_group", "intent", "priority", "impressions_sc", "position_sc", "ctr_sc", "reason"])
        empty.to_csv(output_path, index=False, encoding="utf-8-sig")
        return empty

    def suggested_group(row):
        term = row["term_key"]
        for pattern in PRIORITY_PRODUCT_PATTERNS:
            if pattern in term:
                return f"Search | Exata | {pattern.title()}"
        if row.get("intent") == "COMPRADOR": return "Search | Exata | Compradores Non-Branded"
        if row.get("intent") == "PESQUISADOR/COMPARADOR": return "Search | Teste | Conteúdo/Comparação"
        return "Search | Teste | Oportunidades Search Console"

    df["keyword"] = df["term_key"].apply(lambda x: f"[{x}]")
    df["match_type"] = "EXACT"
    df["suggested_ad_group"] = df.apply(suggested_group, axis=1)
    df["suggested_copy_angle"] = df["intent"].map({
        "COMPRADOR": "Oferta direta, benefício do produto e prova de valor",
        "PESQUISADOR/COMPARADOR": "Educação, comparação e prova social",
        "AMBÍGUA": "Teste de intenção com copy específica",
    }).fillna("Copy alinhada à intenção da busca")

    cols = ["keyword", "match_type", "suggested_ad_group", "suggested_copy_angle", "intent", "priority", "impressions_sc", "position_sc", "ctr_sc", "opportunity_score", "estimated_revenue_potential_new_kw", "reason"]
    df = df[[c for c in cols if c in df.columns]]
    df = df.sort_values(["opportunity_score", "impressions_sc"], ascending=False)

    # Deduplica por tema: se um termo é subconjunto de palavras de outro já selecionado,
    # agrupa como variação em vez de criar linha separada.
    def _words(term: str) -> set:
        return set(str(term).lower().replace("[", "").replace("]", "").split())

    kept_indices: list[int] = []
    variations_map: dict[int, list[str]] = {}

    for idx, row in df.iterrows():
        words_current = _words(row["keyword"])
        merged = False
        for rep_idx in kept_indices:
            words_rep = _words(df.loc[rep_idx, "keyword"])
            # É variação se compartilha ≥60% das palavras com o representante
            overlap = len(words_current & words_rep) / max(len(words_current | words_rep), 1)
            if overlap >= 0.5:
                variations_map.setdefault(rep_idx, []).append(
                    row["keyword"].replace("[", "").replace("]", "")
                )
                merged = True
                break
        if not merged:
            kept_indices.append(idx)

    df = df.loc[kept_indices].copy()
    df["keyword_variations"] = df.index.map(
        lambda i: "; ".join(variations_map[i]) if i in variations_map else ""
    )
    df = df.reset_index(drop=True)

    cols_final = ["keyword", "keyword_variations", "match_type", "suggested_ad_group", "suggested_copy_angle", "intent", "priority", "impressions_sc", "position_sc", "ctr_sc", "opportunity_score", "estimated_revenue_potential_new_kw", "reason"]
    df = df[[c for c in cols_final if c in df.columns]]
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df


def merge_ads_and_search_console(
    ads_csv_path: str,
    search_console_csv_path: str,
    campaign_constraints_csv_path: "str | None" = None,
    output_path: str = "paid_organic_opportunity_analysis.csv",
    breakdown_output_path: str = "paid_organic_term_breakdown.csv",
    new_keywords_output_path: str = "new_keyword_suggestions.csv",
    ads_term_col: str = "search_term",
    sc_term_col: str = "query",
    min_sc_impressions: int = 10,
    min_ads_cost_or_clicks: "tuple[float, int]" = (1.0, 1),
) -> pd.DataFrame:
    ads_raw = pd.read_csv(ads_csv_path)
    sc_raw = pd.read_csv(search_console_csv_path)

    campaign_is = None
    if campaign_constraints_csv_path:
        try:
            constraints = pd.read_csv(campaign_constraints_csv_path)
            is_cols = [c for c in ["campaign_name", "search_budget_lost_impression_share", "search_rank_lost_impression_share"] if c in constraints.columns]
            if "campaign_name" in is_cols and len(is_cols) >= 2:
                campaign_is = constraints[is_cols].copy()
        except Exception:
            pass

    ads = prepare_ads_terms(ads_raw, campaign_is=campaign_is, ads_term_col=ads_term_col)
    ads_breakdown = prepare_ads_breakdown(ads_raw, campaign_is=campaign_is, ads_term_col=ads_term_col)
    sc = prepare_search_console_terms(sc_raw, sc_term_col=sc_term_col, min_sc_impressions=min_sc_impressions)
    merged = ads.merge(sc, on="term_key", how="outer")
    min_cost, min_clicks = min_ads_cost_or_clicks
    merged = merged[(merged["cost_ads"].fillna(0) >= min_cost) | (merged["clicks_ads"].fillna(0) >= min_clicks) | (merged["conversions_ads"].fillna(0) > 0) | (merged["impressions_sc"].fillna(0) >= min_sc_impressions)].copy()
    classifications = merged.apply(classify_paid_organic_opportunity, axis=1, result_type="expand")
    result = pd.concat([merged, classifications], axis=1)
    result["ads_breakdown_summary"] = result["term_key"].apply(lambda term: summarize_breakdown_for_term(term, ads_breakdown))
    def _revenue_upside_50pct(r):
        cpa = safe_float(r.get("cpa_ads"), np.nan)
        cost = safe_float(r.get("cost_ads"), 0)
        if np.isnan(cpa) or cpa > 20 or cost < 5:
            return None
        return round(cost * 0.5 / cpa * TICKET_MEDIO, 2)

    def _kw_revenue_potential(r):
        if r.get("recommended_action") not in ("sugerir_nova_keyword_exata", "testar_google_ads_e_otimizar_seo"):
            return None
        return round(safe_float(r.get("impressions_sc"), 0) * 0.08 * 0.04 * TICKET_MEDIO, 2)

    result["revenue_upside_50pct_scale"] = result.apply(_revenue_upside_50pct, axis=1)
    result["estimated_revenue_potential_new_kw"] = result.apply(_kw_revenue_potential, axis=1)

    result["_priority_order"] = result["priority"].map(PRIORITY_ORDER).fillna(9)
    result = result.sort_values(by=["_priority_order", "opportunity_score", "cost_ads", "impressions_sc"], ascending=[True, False, False, False]).drop(columns=["_priority_order"])
    result.to_csv(output_path, index=False, encoding="utf-8-sig")
    ads_breakdown = ads_breakdown[ads_breakdown["term_key"].isin(set(result["term_key"].dropna()))].copy()
    ads_breakdown.to_csv(breakdown_output_path, index=False, encoding="utf-8-sig")
    generate_new_keyword_suggestions(result, output_path=new_keywords_output_path)
    return result


def create_top_actions(analysis_csv_path: str = "paid_organic_opportunity_analysis.csv", output_path: str = "paid_organic_top_actions.csv", limit: int = 30) -> pd.DataFrame:
    df = pd.read_csv(analysis_csv_path)
    actionable = df[df["recommended_action"].isin([
        "escalar_budget_com_controle", "escalar_pago_e_otimizar_seo", "escalar_pago_com_controle",
        "sugerir_nova_keyword_exata", "revisar_ou_negativar_com_cautela", "testar_google_ads_e_otimizar_seo",
        "revisar_intencao_copy_e_landing", "otimizar_seo_snippet_e_landing", "avaliar_economia_de_midia",
        "proteger_branded_e_monitorar_incrementalidade",
    ])].copy()
    actionable["_priority_order"] = actionable["priority"].map(PRIORITY_ORDER).fillna(9)
    actionable = actionable.sort_values(by=["_priority_order", "opportunity_score", "cost_ads", "impressions_sc"], ascending=[True, False, False, False]).drop(columns=["_priority_order"])
    actionable.head(limit).to_csv(output_path, index=False, encoding="utf-8-sig")
    return actionable.head(limit)
