# Resumo dos resultados técnicos

Este arquivo consolida saídas computacionais para apoiar o relatório futuro; não é o relatório acadêmico.

## Protocolo

- 7.723 cursos com pelo menos 10 notas válidas.
- 6.178 cursos no treino e 1.545 no teste.
- Limiar do alvo: 46,816228, mediana calculada apenas no treino.
- 5 folds estratificados e `random_state=42`.
- Modelos avançados ajustados por `RandomizedSearchCV` no treino.
- Critério de seleção: maior F1 médio de validação cruzada.

## Métricas observadas

| Modelo | F1 CV (média ± DP) | Accuracy teste | Precision teste | Recall teste | F1 teste | ROC-AUC teste |
|---|---:|---:|---:|---:|---:|---:|
| Regressão Logística | 0,8607 ± 0,0128 | 0,8738 | 0,8626 | 0,8944 | 0,8782 | 0,9454 |
| HistGradientBoosting | 0,8541 ± 0,0119 | 0,8583 | 0,8584 | 0,8639 | 0,8611 | 0,9361 |
| Random Forest | 0,8349 ± 0,0085 | 0,8311 | 0,8237 | 0,8499 | 0,8366 | 0,9201 |

## Modelo selecionado

A Regressão Logística foi selecionada porque obteve o maior F1 médio na validação cruzada do treino. O resultado de teste é reportado somente depois dessa escolha. A superioridade do baseline mostra que, com as features agregadas e o recorte atual, a fronteira linear regularizada generalizou melhor que os modelos baseados em árvores avaliados; maior complexidade não garantiu ganho.

O pipeline completo foi salvo em `models/melhor_modelo.joblib`. Os valores-fonte permanecem em `reports/tables/metricas_modelos.csv`, e os hiperparâmetros em `models/metadata_modelo.json`.

## Limite de interpretação

As métricas medem discriminação do alvo operacional acima da mediana, não qualidade oficial, causalidade ou desempenho individual. A avaliação temporal e entre edições ainda é um próximo passo necessário.

