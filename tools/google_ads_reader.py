import os
import pandas as pd
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()

DATE_RANGE = "LAST_30_DAYS"

def get_google_ads_client():
    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }

    login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    if login_customer_id:
        config["login_customer_id"] = login_customer_id.replace("-", "")

    return GoogleAdsClient.load_from_dict(config)


def get_campaigns_last_7_days():
    client = get_google_ads_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID").replace("-", "")

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
          metrics.ctr,
          metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING {DATE_RANGE}
          AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    ga_service = client.get_service("GoogleAdsService")
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    rows = []

    for batch in stream:
        for row in batch.results:
            cost = row.metrics.cost_micros / 1_000_000
            avg_cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0

            rows.append({
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "status": row.campaign.status.name,
                "channel": row.campaign.advertising_channel_type.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost": cost,
                "conversions": row.metrics.conversions,
                "ctr": row.metrics.ctr,
                "avg_cpc": avg_cpc,
            })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["cpa"] = df.apply(
        lambda r: r["cost"] / r["conversions"] if r["conversions"] > 0 else None,
        axis=1
    )

    return df

def _run_gaql(query: str):
    client = get_google_ads_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID").replace("-", "")

    ga_service = client.get_service("GoogleAdsService")
    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    for batch in stream:
        for row in batch.results:
            yield row

def get_ad_groups_last_7_days():
    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          ad_group.id,
          ad_group.name,
          ad_group.status,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.ctr,
          metrics.average_cpc
        FROM ad_group
        WHERE segments.date DURING {DATE_RANGE}
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    rows = []

    for row in _run_gaql(query):
        cost = row.metrics.cost_micros / 1_000_000
        avg_cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0

        rows.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "ad_group_id": row.ad_group.id,
            "ad_group_name": row.ad_group.name,
            "ad_group_status": row.ad_group.status.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": cost,
            "conversions": row.metrics.conversions,
            "ctr": row.metrics.ctr,
            "avg_cpc": avg_cpc,
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["cpa"] = df.apply(
            lambda r: r["cost"] / r["conversions"] if r["conversions"] > 0 else None,
            axis=1
        )

    return df

def get_keywords_last_7_days():
    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          ad_group.id,
          ad_group.name,
          ad_group_criterion.criterion_id,
          ad_group_criterion.keyword.text,
          ad_group_criterion.keyword.match_type,
          ad_group_criterion.status,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.ctr,
          metrics.average_cpc
        FROM keyword_view
        WHERE segments.date DURING {DATE_RANGE}
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
          AND ad_group_criterion.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    rows = []

    for row in _run_gaql(query):
        cost = row.metrics.cost_micros / 1_000_000
        avg_cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0

        rows.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "ad_group_id": row.ad_group.id,
            "ad_group_name": row.ad_group.name,
            "keyword_id": row.ad_group_criterion.criterion_id,
            "keyword": row.ad_group_criterion.keyword.text,
            "match_type": row.ad_group_criterion.keyword.match_type.name,
            "keyword_status": row.ad_group_criterion.status.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": cost,
            "conversions": row.metrics.conversions,
            "ctr": row.metrics.ctr,
            "avg_cpc": avg_cpc,
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["cpa"] = df.apply(
            lambda r: r["cost"] / r["conversions"] if r["conversions"] > 0 else None,
            axis=1
        )

    return df

def get_search_terms_last_7_days():
    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          ad_group.id,
          ad_group.name,
          search_term_view.search_term,
          search_term_view.status,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions,
          metrics.ctr,
          metrics.average_cpc
        FROM search_term_view
        WHERE segments.date DURING {DATE_RANGE}
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    rows = []

    for row in _run_gaql(query):
        cost = row.metrics.cost_micros / 1_000_000
        avg_cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0

        rows.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "ad_group_id": row.ad_group.id,
            "ad_group_name": row.ad_group.name,
            "search_term": row.search_term_view.search_term,
            "search_term_status": row.search_term_view.status.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost": cost,
            "conversions": row.metrics.conversions,
            "ctr": row.metrics.ctr,
            "avg_cpc": avg_cpc,
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["cpa"] = df.apply(
            lambda r: r["cost"] / r["conversions"] if r["conversions"] > 0 else None,
            axis=1
        )

    return df

