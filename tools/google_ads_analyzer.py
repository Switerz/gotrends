import pandas as pd

def classify_campaign_type(campaign_name: str):
    name = campaign_name.lower()

    if "institucional" in name or "brand" in name:
        return "BRANDED"
    else:
        return "NON_BRANDED"

def analyze_search_terms_advanced(df_terms):
    df = df_terms.copy()
    insights = []

    df["campaign_type"] = df["campaign_name"].apply(classify_campaign_type)

    for _, row in df.iterrows():

        campaign_type = row["campaign_type"]

        # =====================
        # BRANDED
        # =====================
        if campaign_type == "BRANDED":

            if row["cost"] > 30 and (row["conversions"] == 0 or pd.isna(row["conversions"])):
                insights.append(
                    f"🚨 [BRANDED] {row['search_term']} gastando sem converter → verificar concorrência ou problema de página"
                )

            elif row["ctr"] < 0.10:
                insights.append(
                    f"⚠️ [BRANDED] CTR baixo em {row['search_term']} → pode ter concorrente roubando clique"
                )

        # =====================
        # NON BRANDED
        # =====================
        else:

            # desperdício
            if row["cost"] > 20 and (row["conversions"] == 0 or pd.isna(row["conversions"])):
                insights.append(
                    f"❌ [NON-BRANDED] {row['search_term']} → negativar (gasto sem conversão)"
                )

            # CPA alto
            elif row["cpa"] and row["cpa"] > 50:
                insights.append(
                    f"💸 [NON-BRANDED] {row['search_term']} → CPA alto (R${row['cpa']:.2f})"
                )

            # oportunidade
            elif row["cpa"] and row["cpa"] < 20:
                insights.append(
                    f"🚀 [NON-BRANDED] {row['search_term']} → escalar / virar keyword exata"
                )

    return insights