# Regras por tipo de campanha

## Search Branded / Institucional

Definição:
- campanhas institucionais;
- termos com “kokeshi”;
- variações próximas de marca.

Targets:
- CPA <= R$10
- ROAS >= 10x
- CPC <= R$0,60

Objetivo:
- proteger demanda de marca;
- capturar usuários de alta intenção;
- evitar perda para concorrentes;
- manter presença em posições críticas.

Sinais de alerta:
- CPA > R$10;
- ROAS < 10x;
- CPC > R$0,60;
- CTR abaixo de 10%;
- CPC subindo;
- termo branded sem conversão;
- presença de concorrente ou termo genérico misturado;
- queda de conversão em termo institucional;
- `search_rank_lost_impression_share` acima de 10%;
- baixa presença em top ou absolute top impression share.

Recomendações típicas:
- revisar copy institucional;
- reforçar assets/extensões;
- checar concorrência;
- revisar tROAS/lance se a marca estiver perdendo leilão;
- isolar termos genéricos misturados;
- proteger termos de marca.

Não recomendar:
- negativar termo de marca sem evidência forte;
- reduzir agressivamente orçamento de branded;
- comparar CPA/ROAS de branded com non-branded;
- aumentar budget se budget lost for 0% e a trava for rank.

## Search Non-Branded

Definição:
- termos sem “kokeshi”;
- categorias;
- produtos;
- problemas de pele;
- termos de comparação;
- concorrentes;
- buscas informacionais.

Targets:
- CPA <= R$20
- ROAS >= 3.5x
- CPC <= R$0,60

Objetivo:
- aquisição incremental;
- descobrir termos compradores;
- cortar desperdício;
- transformar bons termos em keywords exatas;
- capturar demanda que SEO ainda não domina.

Sinais de alerta:
- CPA > R$20;
- ROAS < 3.5x;
- CPC > R$0,60;
- custo relevante sem conversão;
- termo pesquisador consumindo verba;
- termos de brinde/cupom sem conversão;
- concorrentes sem conversão;
- rank lost alto em termo que converte;
- budget lost alto em campanha eficiente;
- mistura de intenção no mesmo grupo.

Recomendações típicas:
- sugerir negativas com cautela;
- criar keyword exata para termos vencedores;
- separar grupos por intenção;
- criar landing específica;
- ajustar copy/RSA por linguagem vencedora;
- sugerir budget apenas quando eficiência + budget lost sustentarem;
- usar Search Console para descobrir lacunas de cobertura.

## Shopping

Objetivo:
- capturar intenção de compra via feed;
- escalar produtos com boa eficiência;
- controlar desperdício por categoria/produto.

Targets:
- priorizar ROAS e valor de conversão quando disponíveis;
- usar CPA como fallback quando valor não for confiável.

Sinais de alerta:
- rank lost alto;
- budget lost alto com CPA/ROAS bom;
- produtos prioritários sem cobertura;
- baixa presença em top impression share;
- feed fraco ou genérico;
- produtos de baixa margem consumindo verba.

Recomendações típicas:
- revisar feed;
- segmentar best sellers;
- separar produtos por margem/performance;
- ajustar orçamento se houver eficiência e budget lost;
- melhorar competitividade se rank lost for alto;
- cruzar produtos prioritários com termos orgânicos do Search Console.

## Performance Max

Objetivo:
- escalar via automação e sinais;
- capturar demanda combinada de Search, Shopping, Display e YouTube.

Riscos:
- mistura de topo, meio e fundo;
- pouca transparência;
- dependência de feed e sinais;
- falso positivo em crescimento sem incrementalidade;
- mistura de branded e non-branded.

Recomendações típicas:
- analisar resultado agregado;
- avaliar asset groups e feed;
- separar best sellers;
- separar PMax institucional de PMax non-branded quando possível;
- não confiar cegamente no algoritmo;
- se rank lost/budget lost aparecem, tratar como sinal de restrição, não como diagnóstico completo.

## Demand Gen / YouTube / Display

Objetivo:
- geração de demanda;
- remarketing;
- suporte ao funil;
- validação criativa.

Regras:
- não julgar apenas por CPA direto se o objetivo for topo/meio de funil;
- observar all_conversions quando disponível;
- separar campanhas de conversão direta de campanhas de influência;
- não misturar análise de Search com Display/YouTube sem contexto;
- avaliar qualidade do tráfego e papel no funil.

## Regras transversais

- Branded e non-branded nunca devem ser analisados com o mesmo target.
- Campanhas com “kokeshi” devem ser avaliadas com targets institucionais.
- Campanhas sem “kokeshi” devem ser avaliadas com targets non-branded.
- Produtos prioritários podem justificar testes mesmo quando o dado ainda é inconclusivo.
- Toda ação agressiva precisa de escopo: campanha, grupo, termo ou keyword.
