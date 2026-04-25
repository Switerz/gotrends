# PATCH para tools/google_ads_reader.py
#
# Objetivo:
# adicionar métricas de cobertura, rank e valor às consultas de Google Ads.
#
# 1) Na query GAQL que busca SEARCH TERMS, adicione ao SELECT:
#
#   metrics.conversions_value,
#   metrics.conversions_value_per_cost
#
# Se sua query de search_term_view aceitar estes campos no seu setup, também adicione:
#
#   metrics.search_impression_share,
#   metrics.search_rank_lost_impression_share,
#   metrics.search_budget_lost_impression_share,
#   metrics.search_top_impression_share,
#   metrics.search_absolute_top_impression_share,
#   metrics.search_click_share
#
# Observação:
# algumas métricas de impression share podem funcionar melhor em campaign/ad_group/keyword
# do que em search_term_view. Por isso o projeto agora tem também:
# tools/campaign_constraints_engine.py
#
# 2) Na montagem do dicionário de cada linha, adicione com getattr para não quebrar:
#
#   "conversions_value": float(getattr(row.metrics, "conversions_value", 0) or 0),
#   "conversions_value_per_cost": float(getattr(row.metrics, "conversions_value_per_cost", 0) or 0),
#   "search_impression_share": float(getattr(row.metrics, "search_impression_share", 0) or 0),
#   "search_rank_lost_impression_share": float(getattr(row.metrics, "search_rank_lost_impression_share", 0) or 0),
#   "search_budget_lost_impression_share": float(getattr(row.metrics, "search_budget_lost_impression_share", 0) or 0),
#   "search_top_impression_share": float(getattr(row.metrics, "search_top_impression_share", 0) or 0),
#   "search_absolute_top_impression_share": float(getattr(row.metrics, "search_absolute_top_impression_share", 0) or 0),
#   "search_click_share": float(getattr(row.metrics, "search_click_share", 0) or 0),
#
# 3) Se a query quebrar por incompatibilidade de campo em search_term_view:
# remova as métricas de impression share do search_term_view
# e mantenha essas métricas apenas no campaign_constraints_engine.py.
