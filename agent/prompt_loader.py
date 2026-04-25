from pathlib import Path


AGENT_DIR = Path(__file__).parent

PROMPT_FILES = [
    "system.md",
    "account_context.md",
    "business_rules.md",
    "financial_model.md",
    "forecast_framework.md",
    "campaign_rules.md",
    "intent_taxonomy.md",
    "decision_framework.md",
    "search_console_context.md",
    "organic_paid_decision_framework.md",
    "keyword_expansion_framework.md",
    "insight_patterns.md",
    "action_policy.md",
    "output_format.md",
    "upcoming_campaigns.md",
]


def load_agent_prompt() -> str:
    parts = []

    for file_name in PROMPT_FILES:
        file_path = AGENT_DIR / file_name

        if not file_path.exists():
            parts.append(f"\n\n# WARNING: arquivo não encontrado: {file_name}\n")
            continue

        content = file_path.read_text(encoding="utf-8")

        parts.append(
            f"\n\n<!-- BEGIN {file_name} -->\n"
            f"{content}\n"
            f"<!-- END {file_name} -->"
        )

    return "\n".join(parts)