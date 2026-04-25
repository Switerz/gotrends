from tools.google_ads_reader import get_search_terms_last_7_days

df = get_search_terms_last_7_days()

# garante o nome esperado pelo cruzamento
if "search_term" not in df.columns:
    possíveis = ["term", "query", "search_term_view.search_term"]
    for col in possíveis:
        if col in df.columns:
            df = df.rename(columns={col: "search_term"})
            break

df.to_csv("google_ads_search_terms.csv", index=False, encoding="utf-8-sig")

print("Arquivo salvo: google_ads_search_terms.csv")
print(df.head())
print(df.columns.tolist())