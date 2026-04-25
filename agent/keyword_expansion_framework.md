# Keyword Expansion Framework

## Objetivo

Usar queries do Google Search Console para sugerir novas keywords no Google Ads.

## Por que usar Search Console

Search Console mostra queries reais em que o site já aparece no Google.

Isso permite descobrir:
- demanda orgânica ainda não capturada por mídia paga;
- termos com intenção comercial;
- produtos/categorias com potencial;
- gaps de SEO que podem ser cobertos temporariamente por Ads.

## Regras para sugerir keyword

Uma query pode virar sugestão de keyword quando:
- tem impressões orgânicas relevantes;
- posição orgânica não é forte;
- não há cobertura paga relevante;
- não é ruído;
- não é operador de busca;
- não é busca puramente institucional sem necessidade;
- não é cupom/brinde sem análise de margem.

## Match type sugerido

### Exata
Usar quando:
- termo tem intenção clara;
- termo é produto prioritário;
- termo é comprador;
- termo tem volume orgânico relevante.

Formato:
- `[termo]`

### Frase
Usar futuramente quando:
- houver cluster de termos similares;
- ainda não houver volume suficiente para exata;
- intenção for boa, mas variações forem importantes.

## Priorização

### Alta prioridade
- produto prioritário;
- intenção compradora;
- muitas impressões;
- posição orgânica ruim;
- baixa cobertura paga.

### Média prioridade
- comparação;
- pesquisa pré-compra;
- oportunidade de conteúdo + remarketing.

### Baixa prioridade
- termo ambíguo;
- termo muito amplo;
- termo informacional sem sinal comercial.

## Output esperado

Toda sugestão deve trazer:
- keyword sugerida;
- match type;
- intenção;
- grupo sugerido;
- ângulo de copy;
- justificativa;
- risco.
