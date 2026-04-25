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

    campaign_constraints = read_csv_records(
        "campaign_constraints_analysis.csv",
        limit=50,
    )

    paid_organic_top_actions = read_csv_records(
        "paid_organic_top_actions.csv",
        limit=30,
    )

    new_keyword_suggestions = read_csv_records(
        "new_keyword_suggestions.csv",
        limit=50,
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
```

# Diagnóstico de restrições por campanha

Use esta seção para entender se a trava de crescimento está em orçamento, rank, cobertura, topo de página ou ausência de gargalo claro.

```json
{json.dumps(campaign_constraints, ensure_ascii=False, indent=2, default=str)}
```

# Top ações cruzando Google Ads + Search Console

Use esta seção como prioridade para recomendações de curto prazo.

```json
{json.dumps(paid_organic_top_actions, ensure_ascii=False, indent=2, default=str)}
```

# Novas keywords sugeridas a partir do Search Console

Use esta seção quando o usuário pedir expansão, novos termos, oportunidades de keyword, grupos de anúncio ou testes de aquisição.

```json
{json.dumps(new_keyword_suggestions, ensure_ascii=False, indent=2, default=str)}
```

# Oportunidades consolidadas por termo

Use esta seção para entender a decisão estratégica por termo.

```json
{json.dumps(paid_organic_opportunities, ensure_ascii=False, indent=2, default=str)}
```

# Breakdown granular por campanha e grupo

Use esta seção para explicar onde manter, revisar, reduzir ou isolar um termo.

```json
{json.dumps(paid_organic_breakdown, ensure_ascii=False, indent=2, default=str)}
```

# Solicitação do usuário

{user_request}
"""
