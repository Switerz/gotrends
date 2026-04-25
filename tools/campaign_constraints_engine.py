import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient


def clean_customer_id(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("-", "").strip()


def get_google_ads_client() -> tuple[GoogleAdsClient, str]:
    load_dotenv()

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }

    login_customer_id = clean_customer_id(os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"))
    customer_id = clean_customer_id(os.getenv("GOOGLE_ADS_CUSTOMER_ID"))

    if login_customer_id:
        config["login_customer_id"] = login_customer_id

    if not customer_id:
        raise ValueError("GOOGLE_ADS_CUSTOMER_ID não encontrado no .env")

    return GoogleAdsClient.load_from_dict(config), customer_id


def safe_float(value, default=0.0) -> float:
    try:
        if value is None:
            return default
        v = float(value)
        return default if pd.isna(v) else v
    except (TypeError, ValueError):
        return default


def money_from_micros(value) -> float:
    return safe_float(value) / 1_000_000


def classify_campaign_type(campaign_name: str, channel_type: str) -> str:
    name = (campaign_name or "").lower()
    channel = (channel_type or "").lower()

    if "brand" in name or "branded" in name or "institucional" in name or "| bd" in name:
        return "BRANDED"
    if "pmax" in name or "performance max" in name or "perform" in name:
        return "PMAX"
    if "shopping" in name:
        return "SHOPPING"
    if "search" in name or "pesquisa" in name or channel == "search":
        return "SEARCH_NON_BRANDED"
    if "display" in name:
        return "DISPLAY"
    if "demand" in name or "youtube" in name or "video" in name:
        return "DEMAND_GEN_VIDEO"
    return channel.upper() or "OUTRO"


_NON_SEARCH_TYPES = {"SHOPPING", "PMAX", "DISPLAY", "DEMAND_GEN_VIDEO"}


def classify_constraint(row: dict) -> tuple[str, str, str]:
    campaign_type = row.get("campaign_type", "")
    conv = safe_float(row.get("conversions"))
    cpa = safe_float(row.get("cpa"), default=999999)
    cost = safe_float(row.get("cost"))

    if campaign_type in _NON_SEARCH_TYPES:
        efficient = conv > 0 and cpa <= 40
        if cost > 0 and not efficient:
            return (
                "NON_SEARCH_LOW_EFFICIENCY",
                "Revisar CPA e ROAS — métricas de IS de Search não se aplicam",
                f"Campanha {campaign_type}: sem conversão ou CPA alto. IS de Search não disponível para este tipo.",
            )
        return (
            "NON_SEARCH_HEALTHY",
            "Monitorar via conversões e ROAS",
            f"Campanha {campaign_type}: sem restrição identificável. IS de Search não se aplica.",
        )

    budget_lost = safe_float(row.get("search_budget_lost_impression_share"))
    rank_lost = safe_float(row.get("search_rank_lost_impression_share"))
    search_is = safe_float(row.get("search_impression_share"))

    efficient = conv > 0 and cpa <= 40

    if budget_lost >= 0.20 and rank_lost >= 0.30:
        if efficient:
            return (
                "BUDGET_AND_RANK_LIMITED",
                "Redistribuir orçamento com cautela e atacar rank ao mesmo tempo",
                "Há perda por orçamento e por rank em campanha com conversão/CPA aceitável.",
            )
        return (
            "BUDGET_AND_RANK_LIMITED_BUT_NOT_PROVEN",
            "Não aumentar orçamento ainda; revisar eficiência e rank primeiro",
            "Há perda por orçamento e rank, mas a campanha ainda não prova eficiência suficiente.",
        )

    if budget_lost >= 0.20:
        if efficient:
            return (
                "BUDGET_LIMITED",
                "Avaliar aumento ou redistribuição de orçamento",
                "Campanha eficiente está perdendo impressões por orçamento.",
            )
        return (
            "BUDGET_LIMITED_BUT_INEFFICIENT",
            "Não escalar orçamento antes de corrigir eficiência",
            "Há perda por orçamento, mas CPA/conversão não sustentam escala automática.",
        )

    if rank_lost >= 0.50:
        return (
            "HEAVILY_RANK_LIMITED",
            "Melhorar Ad Rank: tROAS/lance, qualidade, relevância, landing e estrutura",
            "A principal trava é rank, não orçamento.",
        )

    if rank_lost >= 0.25:
        return (
            "RANK_LIMITED",
            "Revisar competitividade, qualidade, match type, copy e landing",
            "Há perda relevante por rank.",
        )

    if campaign_type == "BRANDED" and rank_lost > 0.10:
        return (
            "BRANDED_RANK_RISK",
            "Proteger branded: revisar lance/tROAS, qualidade e concorrência",
            "Branded com perda por rank pode indicar risco de concorrência ou baixa força no leilão.",
        )

    if search_is > 0 and search_is < 0.30 and cost > 0:
        return (
            "LOW_COVERAGE",
            "Investigar cobertura: match type, elegibilidade, lances, orçamento e segmentação",
            "Baixa parcela de impressão sem causa dominante explícita.",
        )

    return (
        "HEALTHY_OR_NO_CLEAR_CONSTRAINT",
        "Monitorar; não há gargalo claro de orçamento/rank",
        "Sem perda relevante por orçamento ou rank no período.",
    )


def fetch_campaign_constraints(date_range: str = "LAST_30_DAYS") -> pd.DataFrame:
    client, customer_id = get_google_ads_client()
    service = client.get_service("GoogleAdsService")

    query = f"""
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value,
      metrics.ctr,
      metrics.average_cpc,
      metrics.search_impression_share,
      metrics.search_budget_lost_impression_share,
      metrics.search_rank_lost_impression_share,
      metrics.search_top_impression_share,
      metrics.search_absolute_top_impression_share,
      metrics.search_click_share
    FROM campaign
    WHERE segments.date DURING {date_range}
    ORDER BY metrics.cost_micros DESC
    """

    rows = []
    response = service.search_stream(customer_id=customer_id, query=query)

    for batch in response:
        for row in batch.results:
            cost = money_from_micros(row.metrics.cost_micros)
            conversions = safe_float(row.metrics.conversions)
            cpa = cost / conversions if conversions > 0 else None
            campaign_name = row.campaign.name
            channel = row.campaign.advertising_channel_type.name

            record = {
                "campaign_id": row.campaign.id,
                "campaign_name": campaign_name,
                "campaign_status": row.campaign.status.name,
                "advertising_channel_type": channel,
                "campaign_type": classify_campaign_type(campaign_name, channel),
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost": round(cost, 2),
                "conversions": conversions,
                "cpa": round(cpa, 2) if cpa is not None else "",
                "conversions_value": safe_float(row.metrics.conversions_value),
                "conversions_value_per_cost": (
                    safe_float(row.metrics.conversions_value) / cost
                    if cost > 0
                    else 0
                ),
                "ctr": safe_float(row.metrics.ctr),
                "average_cpc": money_from_micros(row.metrics.average_cpc),
                "search_impression_share": safe_float(row.metrics.search_impression_share),
                "search_budget_lost_impression_share": safe_float(row.metrics.search_budget_lost_impression_share),
                "search_rank_lost_impression_share": safe_float(row.metrics.search_rank_lost_impression_share),
                "search_top_impression_share": safe_float(row.metrics.search_top_impression_share),
                "search_absolute_top_impression_share": safe_float(row.metrics.search_absolute_top_impression_share),
                "search_click_share": safe_float(row.metrics.search_click_share),
            }

            constraint_type, recommendation, reason = classify_constraint(record)
            record["constraint_type"] = constraint_type
            record["constraint_recommendation"] = recommendation
            record["constraint_reason"] = reason

            rows.append(record)

    return pd.DataFrame(rows)


def run_campaign_constraints_analysis(
    output_path: str = "campaign_constraints_analysis.csv",
    date_range: str = "LAST_7_DAYS",
) -> pd.DataFrame:
    df = fetch_campaign_constraints(date_range=date_range)

    if df.empty:
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        return df

    priority_order = {
        "BUDGET_AND_RANK_LIMITED": 0,
        "BUDGET_LIMITED": 1,
        "HEAVILY_RANK_LIMITED": 2,
        "BRANDED_RANK_RISK": 3,
        "RANK_LIMITED": 4,
        "LOW_COVERAGE": 5,
        "BUDGET_AND_RANK_LIMITED_BUT_NOT_PROVEN": 6,
        "BUDGET_LIMITED_BUT_INEFFICIENT": 7,
        "HEALTHY_OR_NO_CLEAR_CONSTRAINT": 8,
    }

    df["_priority"] = df["constraint_type"].map(priority_order).fillna(99)
    df = df.sort_values(
        by=["_priority", "conversions", "cost"],
        ascending=[True, False, False],
    ).drop(columns=["_priority"])

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df
