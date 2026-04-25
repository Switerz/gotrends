# Decision Framework

Toda decisão deve seguir esta ordem.

## 1. Tipo de campanha

Classificar como:
- Branded
- Non-branded
- Shopping
- PMax
- Demand Gen / YouTube
- Display

Regra:
- se contém “kokeshi”, tratar como branded/institucional;
- se não contém “kokeshi”, tratar como non-branded, salvo contexto explícito.

## 2. Intenção

Classificar como:
- Comprador
- Pesquisador
- Comparador
- Concorrente / marca terceira
- Caçador de brinde / cupom
- Ambígua

## 3. Performance vs target

Avaliar:
- CPA atual vs target do tipo;
- ROAS atual vs target do tipo;
- CPC atual vs target do tipo;
- conversões;
- custo;
- volume;
- consistência.

Targets:
- Branded: CPA < R$10, ROAS > 10x, CPC < R$0,60
- Non-branded: CPA < R$20, ROAS > 3.5x, CPC < R$0,60

## 4. Demanda e cobertura

Avaliar:
- há demanda orgânica no Search Console?
- o termo aparece mal posicionado organicamente?
- há baixa cobertura paga?
- há nova keyword sugerida?
- a query tem intenção comercial?

## 5. Restrição de escala

Avaliar:
- perde por orçamento?
- perde por rank?
- tem search impression share baixo?
- tem baixa presença no topo?
- gargalo é budget, rank, cobertura, estrutura ou criativo?

## 6. Decisão por cenário

| Cenário | Ação |
|--------|------|
| Branded + CPA <= 10 + ROAS >= 10x | manter/proteger |
| Branded + CPA > 10 | revisar urgentemente |
| Branded + ROAS < 8x | investigar problema |
| Branded + CPC > 0,60 | investigar concorrência/rank |
| Branded + rank lost > 10% | proteger marca e revisar leilão |
| Non-branded + CPA <= 20 + ROAS >= 3.5x | escalar com controle |
| Non-branded + CPA 20–30 | otimizar antes de escalar |
| Non-branded + CPA > 30 | revisar intenção/copy/landing |
| Non-branded + CPA > 40 | isolar, reduzir ou negativar com cautela |
| Non-branded + CPC > 0,60 + CPA ruim | revisar qualidade/match type |
| Comprador + converte bem + budget lost alto | redistribuir/aumentar orçamento com aprovação |
| Comprador + converte bem + rank lost alto | melhorar rank antes de escalar verba |
| Budget lost alto + CPA ruim | não escalar; corrigir eficiência |
| Rank lost alto + CPA bom | revisar lance/tROAS, qualidade, landing e estrutura |
| Search Console com alta impressão + sem cobertura paga | sugerir nova keyword exata |
| Search Console com alta impressão + posição ruim | testar Ads e otimizar SEO |
| Pesquisador + não converte | isolar, reduzir ou criar conteúdo se houver potencial |
| Brinde/cupom + não converte | sugerir negativa com cautela |
| Concorrente + não converte | revisar ou negativar com escopo controlado |
| Termo com gasto alto sem conversão | revisar ou negativar com cautela |
| Mesmo termo bom em um grupo e ruim em outro | ação granular, não exclusão global |

## 7. Prioridade

Alta:
- impacto direto em orçamento;
- desperdício relevante;
- oportunidade eficiente;
- proteção de marca;
- budget/rank lost em campanha eficiente;
- nova keyword com alta demanda e intenção compradora.

Média:
- otimização estrutural;
- cobertura;
- SEO + Ads;
- testes controlados;
- copy/RSA;
- landing.

Baixa:
- monitoramento;
- dados insuficientes;
- baixo volume;
- intenção ambígua.

## 8. Regra de segurança

Toda recomendação deve deixar claro:
- o que fazer;
- onde fazer;
- por que fazer;
- qual métrica sustenta;
- target usado;
- risco de falso positivo;
- se precisa aprovação humana.

## 9. Regra contra conclusões erradas

Nunca concluir que “a conta captura tudo” apenas porque `budget_lost` é 0%.

Para falar em saturação ou ausência de gargalo, avaliar também:
- rank lost;
- search impression share;
- top impression share;
- absolute top impression share;
- cobertura de termos;
- match type;
- status de campanha;
- elegibilidade.
