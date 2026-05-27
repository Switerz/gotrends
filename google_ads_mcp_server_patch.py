from pathlib import Path
import pandas as pd


@mcp.tool()
def get_campaign_constraints_analysis() -> str:
    """
    Retorna diagnóstico de restrições por campanha:
    orçamento, rank, cobertura, topo de página e recomendação de alavanca.
    """
    path = Path("campaign_constraints_analysis.csv")

    if not path.exists():
        return (
            "Arquivo campaign_constraints_analysis.csv não encontrado. "
            "Rode primeiro: python run_campaign_constraints_analysis.py"
        )

    df = pd.read_csv(path).fillna("")

    return df.head(50).to_json(
        orient="records",
        force_ascii=False,
        indent=2,
    )
