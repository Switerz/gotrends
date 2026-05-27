from google.ads.googleads.client import GoogleAdsClient
import os
from dotenv import load_dotenv

load_dotenv()


def clean_customer_id(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("-", "").strip()


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

client = GoogleAdsClient.load_from_dict(config)

query = """
SELECT
  campaign.name,
  metrics.search_budget_lost_impression_share,
  metrics.search_rank_lost_impression_share
FROM campaign
WHERE segments.date DURING LAST_7_DAYS
"""

service = client.get_service("GoogleAdsService")

response = service.search(
    customer_id=customer_id,
    query=query,
)

for row in response:
    print(
        row.campaign.name,
        "budget_lost:",
        row.metrics.search_budget_lost_impression_share,
        "rank_lost:",
        row.metrics.search_rank_lost_impression_share,
    )