from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_TOKEN_FILE = Path("search_console_token.json")
DEFAULT_CLIENT_SECRET_FILE = Path("client_secret.json")
DEFAULT_SITE_URL = "sc-domain:kokeshi.com.br"


def get_search_console_credentials(
    client_secret_file: str | Path = DEFAULT_CLIENT_SECRET_FILE,
    token_file: str | Path = DEFAULT_TOKEN_FILE,
) -> Credentials:
    """Carrega ou gera credenciais OAuth para leitura do Search Console."""
    client_secret_file = Path(client_secret_file)
    token_file = Path(token_file)

    creds: Credentials | None = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_file.write_text(creds.to_json(), encoding="utf-8")

    if not creds or not creds.valid:
        if not client_secret_file.exists():
            raise FileNotFoundError(
                f"Não encontrei {client_secret_file}. Coloque o OAuth JSON nessa pasta "
                "ou informe client_secret_file."
            )

        flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_file), SCOPES)
        creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")

    return creds


def get_search_console_service(
    client_secret_file: str | Path = DEFAULT_CLIENT_SECRET_FILE,
    token_file: str | Path = DEFAULT_TOKEN_FILE,
):
    creds = get_search_console_credentials(client_secret_file, token_file)
    return build("searchconsole", "v1", credentials=creds)


def list_search_console_sites(
    client_secret_file: str | Path = DEFAULT_CLIENT_SECRET_FILE,
    token_file: str | Path = DEFAULT_TOKEN_FILE,
) -> list[dict[str, Any]]:
    service = get_search_console_service(client_secret_file, token_file)
    response = service.sites().list().execute()
    return response.get("siteEntry", [])


def get_search_console_queries(
    site_url: str = DEFAULT_SITE_URL,
    start_date: str = "2026-04-01",
    end_date: str = "2026-04-23",
    row_limit: int = 25000,
    dimensions: list[str] | None = None,
    client_secret_file: str | Path = DEFAULT_CLIENT_SECRET_FILE,
    token_file: str | Path = DEFAULT_TOKEN_FILE,
) -> pd.DataFrame:
    """
    Retorna dados de Search Analytics em DataFrame.

    dimensions comuns:
    - ["query"]
    - ["query", "page"]
    - ["query", "date"]
    - ["query", "country", "device"]
    """
    if dimensions is None:
        dimensions = ["query"]

    service = get_search_console_service(client_secret_file, token_file)

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "type": "web",
    }

    response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    rows = response.get("rows", [])

    parsed_rows: list[dict[str, Any]] = []
    for row in rows:
        keys = row.get("keys", [])
        parsed = {dim: keys[i] if i < len(keys) else None for i, dim in enumerate(dimensions)}
        parsed.update(
            {
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0.0),
                "position": row.get("position", None),
            }
        )
        parsed_rows.append(parsed)

    df = pd.DataFrame(parsed_rows)

    if not df.empty:
        df = df.sort_values(["impressions", "clicks"], ascending=False).reset_index(drop=True)

    return df


def classify_search_console_opportunity(df: pd.DataFrame) -> pd.DataFrame:
    """Cria uma classificação simples de oportunidade orgânica por query."""
    if df.empty:
        return df

    out = df.copy()

    def classify(row: pd.Series) -> str:
        impressions = row.get("impressions", 0) or 0
        ctr = row.get("ctr", 0) or 0
        position = row.get("position", 99) or 99

        if impressions >= 500 and position > 5 and ctr < 0.03:
            return "oportunidade_ads_e_seo"
        if impressions >= 500 and position <= 2 and ctr >= 0.10:
            return "organico_forte"
        if impressions >= 200 and position > 10:
            return "demanda_sem_ranking"
        if impressions < 50:
            return "baixo_sinal"
        return "monitorar"

    out["organic_signal"] = out.apply(classify, axis=1)
    out["ctr_%"] = (out["ctr"] * 100).round(2)
    out["position"] = out["position"].round(2)
    return out


if __name__ == "__main__":
    print("=== Sites disponíveis ===")
    for site in list_search_console_sites():
        print(f"- {site.get('siteUrl')} | {site.get('permissionLevel')}")

    print("\n=== Top queries ===")
    df_queries = get_search_console_queries()
    df_queries = classify_search_console_opportunity(df_queries)
    print(df_queries.head(30).to_string(index=False))
