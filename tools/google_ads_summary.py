import pandas as pd


def generate_summary(df_terms: pd.DataFrame):
    if df_terms.empty:
        return "Sem dados disponíveis."

    df = df_terms.copy()

    # Top desperdício
    waste = df[
        (df["cost"] >= 20) &
        ((df["conversions"] == 0) | (df["conversions"].isna()))
    ].sort_values("cost", ascending=False).head(5)

    # Top oportunidades
    opp = df[
        (df["conversions"] > 0) &
        (df["cpa"].notna())
    ].sort_values("cpa").head(5)

    # CTR ruim
    low_ctr = df[
        (df["impressions"] > 100) &
        (df["ctr"] < 0.01)
    ].head(5)

    summary = []

    summary.append("🚨 PRINCIPAIS DESPERDÍCIOS:")
    for _, row in waste.iterrows():
        summary.append(
            f"- {row['search_term']} (R${row['cost']:.2f} sem conversão)"
        )

    summary.append("\n🚀 OPORTUNIDADES DE ESCALA:")
    for _, row in opp.iterrows():
        summary.append(
            f"- {row['search_term']} (CPA R${row['cpa']:.2f})"
        )

    summary.append("\n⚠️ PROBLEMAS DE CTR:")
    for _, row in low_ctr.iterrows():
        summary.append(
            f"- {row['search_term']} (CTR {row['ctr']:.2%})"
        )

    return "\n".join(summary)