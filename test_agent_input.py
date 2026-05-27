from agent.build_agent_input import build_agent_input

prompt = build_agent_input(
    "Faça uma análise completa das campanhas e priorize ações para amanhã."
)

checks = [
    "# Top ações cruzando Google Ads + Search Console",
    "# Novas keywords sugeridas a partir do Search Console",
    "# Oportunidades consolidadas por termo",
    "# Breakdown granular por campanha e grupo",
    "search_budget_lost_impression_share",
    "new_keyword_suggestions",
]

print("\n=== CHECKS ===")
for item in checks:
    print(f"{item}: {'OK' if item in prompt else 'NÃO ENCONTRADO'}")

print("\nTamanho total:", len(prompt))

print("\n=== TRECHO DAS NOVAS KEYWORDS ===")
idx = prompt.find("# Novas keywords sugeridas a partir do Search Console")
print(prompt[idx:idx + 3000] if idx != -1 else "Seção não encontrada")