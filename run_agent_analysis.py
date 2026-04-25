from tools.google_ads_growth_engine import run_google_ads_growth_analysis

result = run_google_ads_growth_analysis()

print("\n=== RESUMO DA CONTA ===")
print(result["summary"])

print("\n=== TOP AÇÕES ===")
for action in result["top_actions"]:
    print(action)