# Regras de Negócio

## Objetivo de negócio

Maximizar receita com eficiência, sem perder escala e sem tomar decisões agressivas sem evidência suficiente.

O agente deve equilibrar:
- eficiência financeira;
- intenção de busca;
- demanda orgânica;
- cobertura paga;
- estrutura de campanha;
- risco de falso positivo.

## Unit Economics

- Ticket médio: R$90
- LTV médio: R$100
- CPA máximo sustentável geral: até R$20
- CPA acima de R$30: risco de LTV negativo dependendo da margem
- CPA acima de R$40: risco alto
- CPA acima de R$50: desperdício provável, salvo contexto estratégico

## Targets por tipo de termo/campanha

### Branded / Institucional

Definição:
- termo, keyword, campanha ou grupo contendo “kokeshi”;
- campanhas institucionais;
- buscas de marca e variações próximas.

Targets:
- CPA alvo: menor que R$10
- ROAS alvo: maior que 10x
- CPC médio alvo: menor que R$0,60

Interpretação:
- CPA <= R$10: esperado para branded
- CPA entre R$10 e R$15: alerta leve
- CPA > R$15: problema claro
- ROAS >= 10x: esperado
- ROAS entre 8x e 10x: atenção
- ROAS < 8x: investigar
- ROAS < 5x: problema grave
- CPC > R$0,60: investigar concorrência, rank, qualidade e estrutura

Regra crítica:
- branded deve ser sempre mais eficiente que non-branded;
- não usar target de non-branded para justificar CPA ruim em branded;
- não reduzir branded agressivamente apenas porque o orgânico é forte;
- branded tem papel defensivo e estratégico.

### Non-Branded / Não institucional

Definição:
- termos que não contêm “kokeshi”;
- termos genéricos;
- termos de categoria;
- termos de produto;
- termos de comparação;
- termos de concorrente;
- termos informacionais ou de descoberta.

Targets:
- CPA alvo: menor que R$20
- ROAS alvo: maior que 3.5x
- CPC médio alvo: menor que R$0,60

Interpretação:
- CPA <= R$20: eficiente, candidato a escala
- CPA entre R$20 e R$30: aceitável, otimizar antes de escalar
- CPA > R$30: risco, revisar intenção/copy/landing
- CPA > R$40: crítico, isolar, reduzir ou negativar com cautela
- ROAS >= 3.5x: saudável
- ROAS entre 3x e 3.5x: atenção
- ROAS < 3x: risco
- ROAS < 2x: provável inviabilidade
- CPC > R$0,60: investigar concorrência, match type, qualidade e estrutura

## Regras de CPA

- CPA ótimo geral: até R$20
- CPA aceitável geral: até R$30
- CPA crítico: acima de R$40
- Termos com CPA abaixo do target do seu tipo são candidatos a escala.
- Termos acima do target do seu tipo não devem ser escalados sem justificativa adicional.

## Regras de ROAS

Quando `conversions_value_per_cost` estiver confiável, usar ROAS como sinal preferencial.

Referências:
- Branded esperado: ROAS > 10x
- Non-branded esperado: ROAS > 3.5x
- ROAS > 7.5x: excelente para non-branded
- ROAS entre 4.5x e 7.5x: saudável
- ROAS entre 3x e 4.5x: atenção
- ROAS abaixo de 3x: risco
- ROAS abaixo de 1.8x: provavelmente inviável

Quando valor de conversão estiver ausente, zerado ou inconsistente:
- usar CPA;
- usar ticket médio;
- usar LTV;
- sinalizar limitação da análise.

## Regras de CPC

CPC médio alvo:
- Branded: menor que R$0,60
- Non-branded: menor que R$0,60

Interpretação:
- CPC alto com CPA bom pode ser aceitável se houver conversão e margem.
- CPC alto com CPA ruim indica problema de qualidade, concorrência, match type ou estrutura.
- CPC alto em branded é mais preocupante que em non-branded, pois pode indicar disputa por marca ou perda de rank.

## Produtos prioritários

- creme facial
- olhos de gueixa
- pele de porcelana
- gota de colágeno
- skincare coreano
- sérum facial
- body splash

Regra:
- termos relacionados a produtos prioritários têm prioridade maior;
- se performarem bem, escalar com mais agressividade;
- se tiverem demanda orgânica e baixa cobertura paga, sugerir teste controlado;
- se gastarem sem conversão, revisar antes de cortar por serem estratégicos.

## Categorias prioritárias

- skincare
- hidratação facial
- kits
- beleza coreana
- anti-idade
- pele oleosa
- renovadores
- body splash

Regra:
- identificar clusters por categoria;
- sugerir agrupamento por intenção + categoria;
- evitar misturar pesquisador, comprador, comparador e brinde no mesmo grupo.

## Regras de orçamento

Aumentar orçamento é ação de alto risco.

Só sugerir aumento ou redistribuição quando houver:
- conversão;
- CPA dentro do target do tipo;
- ROAS saudável;
- perda por orçamento;
- ou oportunidade clara de captura com demanda comprovada.

Se `search_rank_lost_impression_share` também for alto:
- budget sozinho não resolve;
- a recomendação deve combinar orçamento com melhoria de rank.

Se `search_budget_lost_impression_share` for 0:
- não recomendar aumento de budget como primeira alavanca;
- investigar rank, cobertura, match type, tROAS/lance, qualidade, feed e estrutura.

## Regras de rank

Rank lost alto indica limitação por competitividade/qualidade.

Melhorias possíveis:
- ajuste de tROAS/lance;
- melhora de qualidade/relevância do anúncio;
- assets/extensões;
- landing page;
- estrutura por intenção;
- match type;
- feed em Shopping/PMax;
- separação de termos compradores e pesquisadores.

## Regras de Search Console

Search Console representa demanda orgânica real do site.

Usar Search Console para:
- descobrir novas keywords;
- identificar termos com demanda mas baixa captura orgânica;
- priorizar SEO + Ads;
- encontrar termos que o site já domina organicamente;
- cruzar demanda orgânica com performance paga.

Não usar Search Console para:
- concluir conversão;
- cortar termo pago sozinho;
- substituir dados de Google Ads.

## Regras de novas keywords

Uma query do Search Console pode virar nova keyword quando:
- tem impressões orgânicas relevantes;
- posição orgânica não é forte;
- não há cobertura paga relevante;
- intenção é compradora, comparadora ou produto prioritário;
- não é ruído, operador, cupom sem margem ou termo irrelevante.

Preferência:
- keyword exata para termos claros e próximos da compra;
- teste controlado para termos informacionais/comparadores;
- landing ou conteúdo para termos de pesquisa.

## Guardrails

- Nunca executar mudanças automaticamente.
- Nunca negativar automaticamente.
- Nunca criar keyword automaticamente.
- Nunca aumentar orçamento automaticamente.
- Toda recomendação de alto risco deve trazer justificativa, métrica, escopo e risco.
