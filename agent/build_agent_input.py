import json
from pathlib import Path

import pandas as pd

from agent.prompt_loader import load_agent_prompt
from tools.google_ads_growth_engine import run_google_ads_growth_analysis


def read_csv_records(file_path: str, limit: int = 30) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        return []

    df = pd.read_csv(path).fillna("")
    return df.head(limit).to_dict(orient="records")


def build_agent_input(user_request: str) -> str:
    agent_prompt = load_agent_prompt()
    google_ads_analysis = run_google_ads_growth_analysis()

    paid_organic_top_actions = read_csv_records(
        "paid_organic_top_actions.csv",
        limit=30,
    )

    paid_organic_opportunities = read_csv_records(
        "paid_organic_opportunity_analysis.csv",
        limit=50,
    )

    paid_organic_breakdown = read_csv_records(
        "paid_organic_term_breakdown.csv",
        limit=80,
    )

    return f"""
{agent_prompt}

# Dados atuais extraídos do Google Ads

```json
{json.dumps(google_ads_analysis, ensure_ascii=False, indent=2, default=str)}