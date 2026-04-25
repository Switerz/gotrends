from tools.google_ads_reader import (
    get_campaigns_last_7_days,
    get_ad_groups_last_7_days,
    get_keywords_last_7_days,
    get_search_terms_last_7_days,
)
from tools.google_ads_terms_analyzer import analyze_search_terms
from tools.google_ads_summary import generate_summary


def google_ads_healthcheck():
    df_campaigns = get_campaigns_last_7_days()
    df_adgroups = get_ad_groups_last_7_days()
    df_keywords = get_keywords_last_7_days()
    df_terms = get_search_terms_last_7_days()

    return {
        "campaigns_rows": len(df_campaigns),
        "adgroups_rows": len(df_adgroups),
        "keywords_rows": len(df_keywords),
        "search_terms_rows": len(df_terms),
        "total_cost": float(df_campaigns["cost"].sum()) if not df_campaigns.empty else 0,
        "total_conversions": float(df_campaigns["conversions"].sum()) if not df_campaigns.empty else 0,
    }


def analyze_google_ads_account():
    df_terms = get_search_terms_last_7_days()
    df_analysis = analyze_search_terms(df_terms)
    summary = generate_summary(df_terms)

    return {
        "summary": summary,
        "table": df_analysis.head(50).to_dict(orient="records"),
    }