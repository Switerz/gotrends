# Framework de Forecast

## Objetivo

Traduzir recomendações táticas em impacto financeiro projetado.
Toda recomendação deve ter: ação → impacto estimado → horizonte → confiança.

## Cenários de Otimização

Sempre apresentar com base nos dados reais do período analisado:

### Cenário Conservador
- Ação: cortar apenas termos com CPA > R$50 (inviáveis)
- Reinvestimento: 50% do budget liberado nos top performers
- Conversões adicionais: `(wasted_spend_cpa50 × 0.5) / account_cpa`
- Receita adicional: conversões adicionais × R$90

### Cenário Base
- Ação: cortar CPA > R$50 + revisar CPA > R$40
- Reinvestimento: 75% do budget liberado
- Conversões adicionais: `(wasted_spend_cpa40 × 0.75) / account_cpa`
- Receita adicional: conversões adicionais × R$90

### Cenário Otimista
- Ação: cortar todos os termos fora de meta + negativar sem conversão com gasto > R$20
- Reinvestimento: 100% do budget liberado
- Conversões adicionais: `(wasted_spend_cpa40 × 1.0) / account_cpa`
- Receita adicional: conversões adicionais × R$90

## Formato Obrigatório de Tabela de Forecast

| Métrica | Atual (30d) | Conservador | Base | Otimista |
|---|---|---|---|---|
| Budget | R$X | R$X | R$X | R$X |
| Conversões | N | N+x | N+y | N+z |
| Receita estimada | R$X | R$X | R$X | R$X |
| CPA médio | R$X | R$X | R$X | R$X |
| ROAS estimado | Xx | Xx | Xx | Xx |
| Receita adicional | — | R$X | R$X | R$X |

## Como Calcular Projeção de Escala de um Termo

Exemplo com `kokeshi` (CPA R$3,27, 2.275 conv, R$7.431 gasto):

1. Budget atual: R$7.431
2. Projeção com 2x budget (R$14.862): CPA sobe ~12% → R$3,66
3. Conversões adicionais: R$7.431 / R$3,66 = ~2.030
4. Receita adicional: 2.030 × R$90 = R$182.700
5. ROI do investimento incremental: R$182.700 / R$7.431 = 24.6x

Sempre mostrar o cálculo explícito.

## Regras de Forecast Realista

1. Nunca assumir eficiência constante em escala — CPA degrada com volume
2. Para corte de termos: a economia é certa; a reabsorção pelo algoritmo leva 7-14 dias
3. Sinalizar nível de confiança baseado no volume de conversões:
   - Alta confiança: > 10 conversões no período
   - Média confiança: 3 a 10 conversões
   - Baixa confiança: < 3 conversões — não usar para decisões de corte
4. Não misturar LTV com receita da primeira compra — deixar explícito qual está sendo usado
5. Sinalizar se o período analisado pode ser atípico (promoções, sazonalidade)

## Horizonte de Tempo das Recomendações

- **7 dias**: impacto de cortes, negativações e pausas
- **30 dias**: impacto de escala de budget e novos grupos/keywords
- **90 dias**: impacto de reestruturação, keywords exatas, nova copy

## O Que NÃO Fazer no Forecast

- Não projetar receita sem mostrar o CPA assumido
- Não ignorar a curva de aprendizado do algoritmo ao cortar termos
- Não apresentar forecast sem separar o que é dado real vs estimativa
- Não usar LTV como justificativa para CPA inviável sem evidência de recompra
