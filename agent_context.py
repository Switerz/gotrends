ACCOUNT_CONTEXT = {
    "brand_name": "Kokeshi",  # ajuste se necessário
    "currency": "BRL",

    "campaign_rules": {
        "branded": {
            "identifier": ["institucional", "brand", "branded"],
            "target_roas": 25.0,  # 2500%
            "goal": "capturar demanda de marca com máxima eficiência",
            "risk": "perder tráfego de alta intenção ou deixar concorrentes capturarem buscas da marca",
        },
        "non_branded": {
            "identifier": ["soluções", "non-branded", "nbd", "nb"],
            "target_roas": 2.4,  # 240%
            "goal": "capturar demanda incremental com eficiência",
            "risk": "gastar com termos amplos, curiosos ou de baixa intenção",
        },
    },

    "guardrails": {
        "allow_auto_changes": False,
        "allowed_actions": [
            "analisar",
            "recomendar",
            "priorizar",
            "gerar relatório",
            "sugerir negativos",
            "sugerir novas keywords exatas",
        ],
        "blocked_actions": [
            "pausar campanha",
            "alterar orçamento",
            "alterar tROAS",
            "negativar termo automaticamente",
        ],
    },
}