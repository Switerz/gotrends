import pandas as pd


def analyze_search_terms(df_terms: pd.DataFrame):
    if df_terms.empty:
        return pd.DataFrame()

    df = df_terms.copy()

    df["decision"] = "MANTER"
    df["reason"] = "Sem alerta relevante"

    # 1. Gastou e não converteu
    mask_waste = (df["cost"] >= 20) & ((df["conversions"] == 0) | (df["conversions"].isna()))
    df.loc[mask_waste, "decision"] = "NEGATIVAR / REVISAR"
    df.loc[mask_waste, "reason"] = "Custo relevante sem conversão"

    # 2. CPA alto
    cpa_ref = df["cpa"].dropna().median()

    if pd.notna(cpa_ref):
        mask_high_cpa = df["cpa"].notna() & (df["cpa"] > cpa_ref * 2)
        df.loc[mask_high_cpa, "decision"] = "REVISAR"
        df.loc[mask_high_cpa, "reason"] = f"CPA acima de 2x a mediana da conta (ref: R${cpa_ref:.2f})"

    # 3. Termo muito bom
    mask_good = (
        df["conversions"].fillna(0) > 0
    ) & (
        df["cpa"].notna()
    ) & (
        df["cpa"] <= cpa_ref
    )

    df.loc[mask_good, "decision"] = "ESCALAR / CRIAR KEYWORD EXATA"
    df.loc[mask_good, "reason"] = "Termo converte com CPA abaixo ou igual à mediana"

    # 4. CTR baixo com volume
    mask_low_ctr = (df["impressions"] >= 100) & (df["ctr"] < 0.01)
    df.loc[mask_low_ctr, "decision"] = "REVISAR ANÚNCIO / INTENÇÃO"
    df.loc[mask_low_ctr, "reason"] = "CTR baixo com volume relevante"

    cols = [
        "campaign_name",
        "ad_group_name",
        "search_term",
        "cost",
        "clicks",
        "conversions",
        "ctr",
        "avg_cpc",
        "cpa",
        "decision",
        "reason",
    ]

    return df[cols].sort_values(["decision", "cost"], ascending=[True, False])