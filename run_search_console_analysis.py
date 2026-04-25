from tools.google_search_console_reader import (
    DEFAULT_SITE_URL,
    classify_search_console_opportunity,
    get_search_console_queries,
    list_search_console_sites,
)

from datetime import date, timedelta

SITE_URL = DEFAULT_SITE_URL
END_DATE   = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
START_DATE = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")

print("=== PROPRIEDADES DISPONÍVEIS ===")
for site in list_search_console_sites():
    print(f"- {site.get('siteUrl')} | permissão: {site.get('permissionLevel')}")

print("\n=== CONSULTANDO SEARCH CONSOLE ===")
print(f"Site: {SITE_URL}")
print(f"Período: {START_DATE} a {END_DATE}")

df = get_search_console_queries(
    site_url=SITE_URL,
    start_date=START_DATE,
    end_date=END_DATE,
    dimensions=["query"],
    row_limit=25000,
)

df = classify_search_console_opportunity(df)

print("\n=== TOP 30 QUERIES ===")
print(df.head(30).to_string(index=False))

output_file = "search_console_queries_kokeshi.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\nArquivo salvo: {output_file}")
