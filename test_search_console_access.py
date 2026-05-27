from __future__ import annotations

import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
CLIENT_SECRET_FILE = "client_secret.json"  # renomeie seu arquivo OAuth para este nome ou ajuste aqui
TOKEN_FILE = Path("search_console_token.json")


def main() -> None:
    print("=== TESTE DE ACESSO AO GOOGLE SEARCH CONSOLE ===")
    print("Escopo usado:", SCOPES[0])
    print()

    if not Path(CLIENT_SECRET_FILE).exists():
        raise FileNotFoundError(
            f"Não encontrei {CLIENT_SECRET_FILE}. Coloque o arquivo OAuth na mesma pasta "
            "ou ajuste CLIENT_SECRET_FILE no script."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
    )

    creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"Token salvo em: {TOKEN_FILE.resolve()}")
    print()

    service = build("searchconsole", "v1", credentials=creds)

    try:
        sites_response = service.sites().list().execute()
    except HttpError as e:
        print("ERRO AO LISTAR PROPRIEDADES")
        print(e)
        return

    sites = sites_response.get("siteEntry", [])

    if not sites:
        print("Nenhuma propriedade encontrada.")
        print("Possíveis causas:")
        print("- sua conta Google não tem acesso ao Search Console do domínio;")
        print("- você autenticou com a conta errada;")
        print("- a Search Console API não está ativada no projeto Google Cloud.")
        return

    print("Propriedades disponíveis para esta conta:")
    for i, site in enumerate(sites, start=1):
        print(f"{i}. {site.get('siteUrl')} | permissão: {site.get('permissionLevel')}")

    # Teste opcional simples na primeira propriedade listada.
    site_url = sites[0]["siteUrl"]
    print()
    print(f"Testando Search Analytics na primeira propriedade: {site_url}")

    request = {
        "startDate": "2026-04-01",
        "endDate": "2026-04-23",
        "dimensions": ["query"],
        "rowLimit": 10,
        "type": "web",
    }

    try:
        analytics_response = service.searchanalytics().query(
            siteUrl=site_url,
            body=request,
        ).execute()
    except HttpError as e:
        print("Consegui listar propriedades, mas falhei ao consultar Search Analytics.")
        print(e)
        return

    rows = analytics_response.get("rows", [])
    print()
    print("Top queries retornadas:")
    if not rows:
        print("Sem linhas para o período testado. Isso pode ser normal se houver pouco dado recente.")
    else:
        for row in rows:
            query = row.get("keys", [""])[0]
            print({
                "query": query,
                "clicks": row.get("clicks"),
                "impressions": row.get("impressions"),
                "ctr": row.get("ctr"),
                "position": row.get("position"),
            })


if __name__ == "__main__":
    main()
