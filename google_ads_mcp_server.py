import json
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import pandas as pd

from agent.build_agent_input import build_agent_input
from tools.google_ads_growth_engine import run_google_ads_growth_analysis

mcp = FastMCP("google-ads-growth-agent")


@mcp.tool()
def run_google_ads_growth_analysis_tool() -> str:
    """
    Analisa a conta Google Ads com regras de negócio, intenção de busca,
    campanhas branded/non-branded, produtos prioritários e unit economics.
    Retorna resumo e top ações recomendadas.
    """
    result = run_google_ads_growth_analysis()
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


@mcp.tool()
def build_google_ads_agent_prompt(user_request: str) -> str:
    """
    Monta o prompt completo do agente com todos os arquivos markdown,
    dados reais do Google Ads e o pedido do usuário.
    Use esta tool quando quiser uma análise especialista completa.
    """
    return build_agent_input(user_request)

@mcp.tool()
def ask_google_ads_growth_agent(user_request: str) -> str:
    """
    Use esta ferramenta quando o usuário quiser análise, diagnóstico,
    auditoria ou recomendação sobre Google Ads, campanhas, search terms,
    keywords, grupos de anúncio, CPA, ROAS, intenção de busca ou mídia paga.

    A ferramenta carrega automaticamente:
    - todos os arquivos markdown do agente;
    - regras de negócio;
    - contexto da conta;
    - dados reais do Google Ads;
    - análise estruturada.

    Retorna o prompt completo para o Claude responder como especialista.
    """
    return build_agent_input(user_request)

@mcp.tool()
def get_paid_organic_top_actions() -> str:
    """
    Retorna as principais ações cruzando Google Ads e Search Console,
    incluindo recomendação consolidada por termo e breakdown por campanha/grupo.
    """
    path = Path("paid_organic_top_actions.csv")

    if not path.exists():
        return (
            "Arquivo paid_organic_top_actions.csv não encontrado. "
            "Rode primeiro: python run_paid_organic_analysis.py"
        )

    df = pd.read_csv(path).fillna("")

    return df.head(30).to_json(
        orient="records",
        force_ascii=False,
        indent=2,
    )


@mcp.tool()
def get_new_keyword_suggestions() -> str:
    """
    Retorna novas keywords sugeridas a partir de queries do Google Search Console,
    com match type, grupo sugerido, intenção e justificativa.
    """
    path = Path("new_keyword_suggestions.csv")

    if not path.exists():
        return (
            "Arquivo new_keyword_suggestions.csv não encontrado. "
            "Rode primeiro: python run_paid_organic_analysis.py"
        )

    df = pd.read_csv(path).fillna("")

    return df.head(50).to_json(
        orient="records",
        force_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    mcp.run()