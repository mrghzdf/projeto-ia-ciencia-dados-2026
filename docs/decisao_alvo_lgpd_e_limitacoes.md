# Decisão da variável-alvo, LGPD e limitações

## Alvo escolhido

O melhor desfecho original é `NT_GER`, nota geral documentada pelo INEP. Como os arquivos não permitem identificação de estudantes entre tabelas, o desfecho utilizado é `NT_GER_MEDIA_CURSO`, agregado somente entre registros com `TP_PRES=555` e nota presente.

Para cumprir o conjunto solicitado de métricas de classificação, deriva-se `TARGET_ACIMA_MEDIANA_TREINO`:

1. filtram-se cursos com pelo menos 10 resultados válidos;
2. faz-se o split aleatório 80/20 com `random_state=42`;
3. calcula-se a mediana de `NT_GER_MEDIA_CURSO` apenas no treino;
4. classe `1` significa média do curso acima desse limiar; classe `0`, caso contrário;
5. aplica-se o mesmo limiar intocado ao teste.

Esse alvo não significa aprovação, qualidade oficial, Conceito Enade ou regra do INEP. É um recorte operacional reproduzível para comparação de classificadores. Para uso substantivo futuro, recomenda-se também modelar `NT_GER_MEDIA_CURSO` por regressão e reportar intervalos de incerteza ponderados pelo tamanho do curso.

## Prevenção de leakage

- A mediana do alvo é aprendida somente no treino.
- Imputação, limites IQR, padronização e one-hot encoding ficam dentro de `Pipeline`/`ColumnTransformer`.
- Validação cruzada refaz todo o pré-processamento dentro de cada fold.
- Variáveis que compõem ou revelam a nota da prova são excluídas.
- O conjunto de teste é usado uma vez para métricas finais, não para escolher modelo/hiperparâmetro.

## Nulos, outliers e duplicados

- Anos impossíveis informados pelos estudantes são convertidos em nulos, com taxa de erro preservada como feature.
- Numéricas: mediana, clipping por IQR e `StandardScaler`, todos ajustados no treino.
- Categóricas: moda e one-hot com categorias desconhecidas ignoradas no teste.
- Idades 17-89 são válidas conforme o dicionário e não são apagadas na origem.
- Repetições brutas não são removidas sem identificador individual; a unicidade é assegurada somente na tabela curso.

## LGPD, ética e uso responsável

- A fragmentação oficial impede perfis individuais; o projeto preserva essa barreira.
- Sexo, renda, escola anterior e ação afirmativa são atributos de alto risco para decisões. As associações são agregadas e não devem justificar punição, exclusão de recursos ou ranking causal.
- Previsões são sinais exploratórios no nível de curso, não diagnósticos de pessoas nem avaliações oficiais de IES.
- Falso positivo pode direcionar intervenção a curso que não precisava; falso negativo pode deixar de priorizar apoio. A aplicação deve manter revisão humana e auditoria por grupos/regiões.

## XGBoost

O dataset tabular seria compatível com XGBoost, mas o wheel para macOS requer `libomp.dylib`, ausente no computador. Instalar `libomp` via Homebrew alteraria dependência global e violaria as restrições de isolamento. Por isso, foi usada a alternativa nativa `HistGradientBoostingClassifier`, que implementa boosting de histogramas sem exigir mudança global. O erro de compatibilidade foi observado antes do treinamento; não houve instalação de sistema.

## Limitações

- Agregação por curso impede inferência individual e reduz granularidade.
- Dados de uma única edição não testam generalização temporal/data drift.
- Questionários são autorrelatados e sujeitos a não resposta.
- Correlações e importâncias não demonstram causalidade.
- O filtro de 10 resultados melhora estabilidade, mas exclui cursos pequenos.
