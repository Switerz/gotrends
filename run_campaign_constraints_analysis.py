from tools.campaign_constraints_engine import run_campaign_constraints_analysis


if __name__ == "__main__":
    df = run_campaign_constraints_analysis(
        output_path="campaign_constraints_analysis.csv",
        date_range="LAST_7_DAYS",
    )

    print("\n=== ANÁLISE DE RESTRIÇÕES POR CAMPANHA ===")
    print("Arquivo salvo: campaign_constraints_analysis.csv")

    cols = [
        "campaign_name",
        "campaign_type",
        "cost",
        "conversions",
        "cpa",
        "conversions_value_per_cost",
        "search_impression_share",
        "search_budget_lost_impression_share",
        "search_rank_lost_impression_share",
        "search_top_impression_share",
        "search_absolute_top_impression_share",
        "constraint_type",
        "constraint_recommendation",
        "constraint_reason",
    ]

    available = [c for c in cols if c in df.columns]
    print(df[available].head(30).to_string(index=False))
