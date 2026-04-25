# Organic + Paid Decision Framework

## Objetivo

Cruzar Google Ads e Google Search Console para decidir quais termos devem ser:
- escalados;
- testados;
- protegidos;
- otimizados em SEO;
- revisados;
- negativados com cautela;
- transformados em novas keywords.

## Dois níveis de decisão

### 1. Decisão consolidada por termo

Responde: este termo vale a pena para o negócio?

Use para:
- priorizar termos;
- identificar oportunidade;
- identificar desperdício;
- decidir se o termo merece escala, teste, revisão ou cautela;
- identificar novas keywords vindas de demanda orgânica.

### 2. Decisão granular por campanha/grupo

Responde: onde exatamente esse termo está funcionando ou falhando?

Use para:
- manter o grupo/campanha onde o termo performa bem;
- revisar ou reduzir onde o mesmo termo performa mal;
- detectar problema de estrutura, copy ou landing;
- evitar cortar um termo inteiro quando o problema está em apenas uma campanha.

## Regra central

Consolidação decide **o que fazer com o termo**.

Breakdown granular decide **onde fazer a ação**.

## Papel de cada fonte

### Google Ads
Mostra performance paga:
- custo;
- impressões;
- cliques;
- conversões;
- CPA;
- CTR;
- CPC médio;
- perda de impressão por orçamento.

### Google Search Console
Mostra demanda orgânica real do site:
- queries que geram impressão;
- queries que geram clique;
- CTR orgânico;
- posição média orgânica.

## Métrica de restrição de orçamento

`search_budget_lost_impression_share` indica a porcentagem estimada de impressões perdidas na Rede de Pesquisa porque o orçamento estava baixo.

Interpretação:
- se o termo converte e tem CPA bom, perda alta de impressão por orçamento indica oportunidade de escala;
- se o termo não converte, perda alta não deve ser tratada como oportunidade;
- qualquer sugestão de aumento de orçamento deve ser recomendação, não alteração automática.

## Regras de decisão

### 1. Escalar budget com controle

Condição:
- termo tem múltiplas conversões;
- CPA ótimo ou aceitável;
- perda de impressão por orçamento relevante.

Ação:
- sugerir aumento/redistribuição de orçamento;
- priorizar grupos que já convertem;
- manter ação sujeita à aprovação humana.

Prioridade: alta.

### 2. Escalar pago e otimizar SEO

Condição:
- termo tem conversões no Google Ads;
- CPA ótimo ou aceitável;
- Search Console mostra demanda orgânica;
- posição orgânica ainda tem espaço de melhora.

Ação consolidada:
- sugerir escala do termo.

Ação granular:
- manter/escalar campanhas e grupos com CPA bom;
- revisar campanhas e grupos onde o mesmo termo gastou sem converter.

### 3. Sugerir nova keyword exata

Condição:
- query aparece no Search Console;
- tem impressões orgânicas relevantes;
- posição orgânica ruim ou mediana;
- não há cobertura paga relevante;
- não é termo claramente ruim, de operador, ruído ou cupom.

Ação:
- sugerir keyword exata;
- sugerir grupo de anúncio;
- sugerir ângulo de copy;
- classificar intenção.

Prioridade:
- alta para termos compradores ou produtos prioritários;
- média para termos informacionais/comparadores.

### 4. Testar Google Ads e otimizar SEO

Condição:
- Search Console mostra muita impressão;
- posição orgânica ruim ou mediana;
- termo ainda não tem cobertura paga forte.

Ação:
- criar teste pago;
- criar keyword exata;
- revisar landing;
- melhorar conteúdo SEO.

### 5. Revisar intenção, copy e landing

Condição:
- termo tem volume pago;
- Search Console mostra demanda;
- Ads ainda não converte.

Ação consolidada:
- não cortar automaticamente.

Ação granular:
- identificar campanhas/grupos com custo concentrado;
- revisar copy, promessa e landing desses pontos.

### 6. Revisar ou negativar com cautela

Condição:
- custo pago relevante;
- zero conversão;
- baixo sinal orgânico ou termo de concorrente/cupom/baixa intenção.

Ação consolidada:
- termo entra como risco.

Ação granular:
- sugerir negativa apenas no grupo/campanha problemático quando houver mistura de performance;
- sugerir negativa mais ampla apenas quando o termo for ruim em todos os contextos.

### 7. Otimizar SEO snippet e landing

Condição:
- Search Console mostra impressões;
- posição orgânica razoável;
- CTR abaixo do esperado.

Ação:
- revisar title;
- revisar meta description;
- revisar promessa;
- alinhar página à intenção da busca.

### 8. Proteger branded e monitorar incrementalidade

Condição:
- termo branded ou proprietário;
- orgânico forte ou Ads converte.

Ação:
- manter presença;
- monitorar CPC e concorrência;
- revisar extensões/assets;
- avaliar incrementalidade com cautela.

## Cuidados

- Nunca negativar automaticamente.
- Nunca criar keyword automaticamente.
- Nunca aumentar orçamento automaticamente.
- Não reduzir branded agressivamente apenas porque o orgânico é forte.
- Search Console não mede conversão.
- Termos com cupom/desconto podem converter, mas exigem análise de margem.
- Termos de concorrente podem ser oportunidade, mas têm risco maior.
- Se o termo funciona em uma campanha e falha em outra, a recomendação deve ser estrutural, não uma exclusão global.
