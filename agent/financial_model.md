# Modelo Financeiro

## Unit Economics da Conta

- Ticket médio: R$90
- LTV médio: R$100 (1.1x repeat estimado)
- CPA máximo sustentável: R$20 (margem positiva no LTV)
- CPA acima de R$30: risco de LTV negativo dependendo da margem

## Métricas Financeiras por Search Term

### revenue_estimate
Receita estimada gerada pelo termo no período.
Fórmula: `conversions × R$90`
Uso: comparar o retorno real de cada termo.

### roas_estimate
Retorno sobre investimento do termo.
Fórmula: `revenue_estimate / cost`
Referências:
- ROAS > 7.5x → excelente (equivale a CPA < R$12)
- ROAS 4.5x → aceitável (CPA R$20, break-even no LTV)
- ROAS < 3x → risco (CPA > R$30)
- ROAS < 1.8x → inviável (CPA > R$50)

### opportunity_revenue_delta
Calculado apenas para termos com CPA > R$40.
Responde: "quanto a mais de receita teríamos gerado se esse mesmo gasto fosse aplicado em termos eficientes?"
Fórmula: `(cost / account_cpa_ref × R$90) − revenue_estimate`
Valor positivo = receita perdida por ineficiência.

## Tabela de Referência ROAS × CPA

| CPA | ROAS (ticket R$90) | Classificação |
|---|---|---|
| R$4 | 22.5x | Extraordinário |
| R$9 | 10x | Excelente |
| R$12 | 7.5x | Muito bom |
| R$20 | 4.5x | Aceitável (break-even LTV) |
| R$30 | 3x | Risco |
| R$40 | 2.25x | Crítico |
| R$50 | 1.8x | Inviável |
| R$90 | 1x | Prejuízo direto |

## Regra de Escala com Degradação de CPA

Os valores abaixo são heurísticos de mercado — pontos de partida conservadores, não fórmulas derivadas de dados da conta.

- 2x budget → CPA sobe ~12%
- 3x budget → CPA sobe ~20%
- 5x budget → CPA sobe ~35%

A degradação real depende do espaço disponível no leilão. Use o **Search Impression Share** para calibrar:

| Cenário de IS atual | Degradação esperada ao 2x |
|---|---|
| IS < 50% (muito espaço) | ~5% — o algoritmo captura impressões que já quer comprar |
| IS 50–75% (espaço moderado) | ~12% — estimativa conservadora padrão |
| IS > 85% (perto da saturação) | ~25–40% — precisa de volume de busca maior para absorver |

**Como verificar:** no Google Ads, coluna `Parcela de impressões da Rede de Pesquisa` + `Parc. impr. perd. (orçamento)` vs `Parc. impr. perd. (classificação)`. Se a perda é majoritariamente por orçamento, a degradação ao escalar é baixa. Se é por classificação, o algoritmo já está comprando o que consegue — escalar vai custar mais por impressão.

Nunca assumir que a eficiência se mantém constante em escala.

## Aplicação nas Análises

Toda recomendação deve incluir:
1. Receita atual gerada (revenue_estimate)
2. ROAS atual (roas_estimate)
3. Para termos ruins: receita perdida (opportunity_revenue_delta)
4. Para termos bons: projeção de receita adicional com budget aumentado
5. Nível de confiança baseado no volume de conversões do período
