"""
Atualiza todos os dados da conta e publica no GitHub.
Streamlit Cloud detecta o push e recarrega automaticamente.

Uso:
    python refresh_data.py
"""
import subprocess
import sys
from datetime import date


def run(cmd: str, label: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\n❌ Falhou: {cmd}")
        sys.exit(1)


CSVS = [
    "google_ads_search_terms.csv",
    "campaign_constraints_analysis.csv",
    "search_console_queries_kokeshi.csv",
    "paid_organic_opportunity_analysis.csv",
    "paid_organic_term_breakdown.csv",
    "paid_organic_top_actions.csv",
    "new_keyword_suggestions.csv",
]

if __name__ == "__main__":
    print("\n🌸 Kokeshi · Refresh de dados")
    print(f"   Período: últimos 30 dias até {date.today()}\n")

    run("python export_google_ads_search_terms.py",      "1/4 · Search Terms (Google Ads)")
    run("python run_campaign_constraints_analysis.py",   "2/4 · Campanhas e Restrições (Google Ads)")
    run("python run_search_console_analysis.py",         "3/4 · Search Console (orgânico)")
    run("python run_paid_organic_analysis.py",           "4/4 · Análise Pago × Orgânico")

    print(f"\n{'='*50}")
    print("  Publicando no GitHub...")
    print(f"{'='*50}")

    files = " ".join(CSVS)
    today = date.today().strftime("%Y-%m-%d")

    run(f"git add {files}",                                        "git add CSVs")
    run(f'git commit -m "dados: refresh {today} (últimos 30 dias)"', "git commit")
    run("git push",                                                "git push → Streamlit Cloud")

    print("\n✅ Pronto! Streamlit Cloud vai recarregar em instantes.")
    print(f"   Dashboard: https://gotrends-kokeshi.streamlit.app\n")
