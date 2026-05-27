from tools.google_ads_agent_tools import google_ads_healthcheck, analyze_google_ads_account

print("=== HEALTHCHECK ===")
print(google_ads_healthcheck())

print("\n=== ANÁLISE DA CONTA ===")
result = analyze_google_ads_account()

print(result["summary"])

print("\n=== TOP RECOMENDAÇÕES ===")
for row in result["table"][:10]:
    print(row)