from tools.term_opportunity_engine import (
    merge_ads_and_search_console,
    create_top_actions,
)


if __name__ == "__main__":
    result = merge_ads_and_search_console(
        ads_csv_path="google_ads_search_terms.csv",
        search_console_csv_path="search_console_queries_kokeshi.csv",
        campaign_constraints_csv_path="campaign_constraints_analysis.csv",
        output_path="paid_organic_opportunity_analysis.csv",
        breakdown_output_path="paid_organic_term_breakdown.csv",
        new_keywords_output_path="new_keyword_suggestions.csv",
        min_sc_impressions=10,
        min_ads_cost_or_clicks=(1.0, 1),
    )

    top_actions = create_top_actions(
        analysis_csv_path="paid_organic_opportunity_analysis.csv",
        output_path="paid_organic_top_actions.csv",
        limit=30,
    )

    print("\n=== ANÁLISE PAGO + ORGÂNICO GERADA ===")
    print("Arquivo consolidado: paid_organic_opportunity_analysis.csv")
    print("Arquivo granular: paid_organic_term_breakdown.csv")
    print("Top ações: paid_organic_top_actions.csv")
    print("Novas keywords sugeridas: new_keyword_suggestions.csv")

    cols = [
        "term_key",
        "source_match",
        "intent",
        "cost_ads",
        "conversions_ads",
        "cpa_ads",
        "search_budget_lost_impression_share",
        "impressions_sc",
        "position_sc",
        "opportunity_score",
        "recommended_action",
        "priority",
        "reason",
        "ads_breakdown_summary",
    ]
    available_cols = [c for c in cols if c in top_actions.columns]
    print("\nTop ações:")
    print(top_actions[available_cols].to_string(index=False))
