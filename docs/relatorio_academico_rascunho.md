# PROJETO ABP - DO DADO AO VALOR

## Aplicação de Machine Learning para Análise Preditiva do Desempenho dos Cursos no ENADE 2023

**Curso:** Pós-Graduação em Ciência de Dados e Inteligência Artificial
**Disciplina:** Inteligência Artificial para Ciência de Dados - Turma B - 0726
**Dataset escolhido:** Microdados do ENADE 2023
**Fonte:** Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira - INEP
**Modalidade do dado:** Tabular
**Link do dataset:** https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enade
**Link do Repositório Central:** [INSERIR LINK PÚBLICO DO GITHUB OU DRIVE]
**Link do Dashboard:** [INSERIR LINK PÚBLICO DO STREAMLIT OU ANEXAR PDF/CAPTURA DO DASHBOARD]

## Identificação e Governança Técnica

O projeto foi desenvolvido de forma individual. Dessa maneira, o mesmo discente assumiu a responsabilidade pelas etapas de preparação dos dados, análise exploratória, modelagem preditiva, desenvolvimento do dashboard, análise de riscos e elaboração do relatório.

**Discente:** [NOME COMPLETO]
**Matrícula / Registro Acadêmico:** [MATRÍCULA]

---

# 0. Projeto de Inteligência Artificial e Ciência de Dados

## 0.1 Contexto, problema e proposta de valor

A crescente disponibilidade de dados educacionais públicos cria oportunidades para a aplicação de técnicas de Ciência de Dados e Inteligência Artificial no apoio à gestão acadêmica. Nesse contexto, o Exame Nacional de Desempenho dos Estudantes (ENADE) constitui uma importante fonte de dados para análises relacionadas ao desempenho dos cursos superiores brasileiros.

O presente projeto utiliza os Microdados do ENADE 2023 para desenvolver um modelo preditivo capaz de classificar cursos segundo seu desempenho médio, considerando características institucionais, acadêmicas e socioeconômicas agregadas. A pergunta central do projeto é: **é possível utilizar informações disponíveis nos Microdados do ENADE 2023 para identificar padrões associados à probabilidade de um curso apresentar desempenho médio acima da mediana observada no conjunto de treinamento?**

A proposta não pretende criar um novo indicador oficial de qualidade, tampouco substituir os conceitos ou indicadores produzidos pelo INEP. A classificação criada possui finalidade exclusivamente analítica e acadêmica, permitindo avaliar a aplicação de algoritmos de aprendizado supervisionado em um cenário real.

Do ponto de vista de valor, o projeto demonstra como informações públicas podem ser convertidas em evidências úteis à gestão educacional. Em uma possível aplicação institucional, o modelo poderia atuar como mecanismo de apoio à triagem e priorização de análises, permitindo que gestores, coordenações, Núcleos Docentes Estruturantes e Comissões Próprias de Avaliação concentrem esforços nos cursos que demandem maior atenção.

Metodologicamente, o trabalho foi estruturado segundo o fluxo de aquisição, preparação, análise exploratória, modelagem, visualização e discussão dos resultados. Também foram consideradas boas práticas relacionadas à reprodutibilidade, prevenção de vazamento de dados, gestão de riscos e uso responsável de Inteligência Artificial.

---

## 0.2 Aquisição e caracterização dos dados

A base utilizada corresponde aos **Microdados do ENADE 2023**, disponibilizados publicamente pelo Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira - INEP.

O conjunto original é distribuído em arquivo compactado contendo **32 arquivos TXT delimitados por ponto e vírgula**, além de dicionários de dados nos formatos XLSX/ODS e documentação complementar em PDF. Os arquivos de origem possuem 406.294 registros cada, conforme inventário produzido durante a aquisição.

Para atender ao requisito de disponibilização de amostra, foi gerado o arquivo `amostra_arq3_1pct.csv`, contendo **4.062 registros e 44 colunas**, correspondentes a aproximadamente **0,9998%** das 406.294 linhas do arquivo de origem analisado. A amostragem foi determinística, utilizando `random_state=42`.

O dicionário oficial do INEP foi utilizado como referência para interpretação das variáveis. Entre os campos utilizados estão informações sobre curso, instituição, região, modalidade de ensino, perfil etário, situação de trabalho, renda, trajetória escolar e respostas ao questionário socioeconômico.

O pacote não apresenta uma licença convencional de software ou dados. Por esse motivo, sua utilização neste projeto considera sua disponibilização pública pelo INEP e as orientações de proteção constantes na documentação oficial. Antes de eventual redistribuição dos arquivos originais ou derivados, recomenda-se conferir os termos vigentes no portal oficial.

A unidade final de análise adotada foi o **curso**, identificado durante o processamento por `CO_CURSO`. Essa decisão foi necessária porque a estrutura de proteção dos Microdados do ENADE não permite estabelecer, de maneira segura e autorizada, correspondência individual de estudantes entre diferentes arquivos.

---

## 0.3 Objetivo geral

Desenvolver e avaliar um modelo de Machine Learning capaz de classificar cursos presentes nos Microdados do ENADE 2023 segundo a probabilidade de apresentarem média da nota geral acima do limiar definido exclusivamente com os dados de treinamento.

## 0.4 Objetivos específicos

Avaliar a qualidade e estrutura dos dados disponibilizados pelo INEP; realizar limpeza, padronização e engenharia de atributos; produzir análises exploratórias e identificar associações relevantes; comparar um modelo baseline com algoritmos preditivos de maior complexidade; avaliar os modelos por validação cruzada e métricas de classificação; disponibilizar os resultados por meio de dashboard interativo; e discutir limitações, riscos, LGPD, valor institucional e possibilidades futuras de evolução.

---

# 1. Fase 1: Preparação de Dados e Setup Estrutural

## 1.1 Tratamento de Dados e Engenharia Base

A preparação dos dados foi estruturada de modo a preservar a rastreabilidade e reduzir riscos de vieses ou vazamento de informação. Os arquivos originais foram processados separadamente e agregados por `CO_CURSO` antes da integração final. Não foi realizada tentativa de reconstruir perfis individuais de estudantes.

Após a consolidação, foram considerados **7.723 cursos com pelo menos dez resultados válidos de nota geral**. O critério mínimo foi adotado com a finalidade de aumentar a estabilidade das médias calculadas e evitar que cursos com quantidade muito pequena de resultados exercessem influência desproporcional sobre a modelagem.

A nota geral original `NT_GER` foi utilizada como base para construção do desfecho. Foram considerados apenas registros com presença válida e nota disponível. Para cada curso foi calculada a variável contínua `NT_GER_MEDIA_CURSO`.

Posteriormente, foi construída a variável de classificação `TARGET_ACIMA_MEDIANA_TREINO`. O processo foi realizado de forma a evitar vazamento de dados: primeiro ocorreu a separação entre treinamento e teste; somente depois foi calculada a mediana da nota média dos cursos do conjunto de treinamento. O limiar obtido foi **46,8162 pontos**.

A classe `1` representa cursos cuja média de `NT_GER` ficou acima desse limiar, enquanto a classe `0` representa os demais cursos. O mesmo valor, aprendido exclusivamente no treinamento, foi aplicado ao conjunto de teste.

Essa variável não corresponde a aprovação, reprovação, Conceito ENADE ou qualquer classificação oficial do INEP. Trata-se de uma variável operacional criada especificamente para comparar algoritmos de classificação.

No tratamento de dados ausentes, valores numericamente impossíveis em variáveis de ano, como datas inconsistentes informadas em questionários, foram convertidos em valores nulos antes da agregação. As variáveis numéricas foram submetidas à imputação pela mediana e as categóricas à imputação pela moda.

Quanto aos registros duplicados, a tabela final agregada apresentou `CO_CURSO` único, não sendo necessária a remoção de duplicatas nessa unidade de análise. Repetições observadas nos arquivos brutos não foram tratadas automaticamente como duplicidade de pessoas, pois a estrutura disponibilizada pelo INEP não oferece identificador individual que permita essa conclusão.

Para o tratamento de valores extremos numéricos foi implementado um transformador baseado no Intervalo Interquartil, utilizando fator de **1,5 × IQR**. Os limites são aprendidos somente a partir dos dados de treinamento. Idades válidas dentro da faixa oficial foram preservadas.

As variáveis categóricas foram transformadas por `OneHotEncoder`, configurado para ignorar categorias desconhecidas encontradas futuramente no teste ou em inferências. As variáveis numéricas foram padronizadas com `StandardScaler`.

O balanceamento também foi analisado. A prevalência da classe positiva no conjunto de treinamento foi de aproximadamente 0,5000 e no conjunto de teste de 0,5087, caracterizando uma distribuição bastante equilibrada. Os classificadores ainda foram configurados com `class_weight="balanced"` quando aplicável.

Variáveis que poderiam revelar diretamente o resultado da prova foram excluídas dos preditores. Entre elas estão notas parciais, respostas da prova, gabaritos e variáveis diretamente derivadas do resultado, reduzindo o risco de `data leakage`.

---

## 1.2 Estratégia de Isolamento e Escala

A base com 7.723 cursos foi dividida em **80% para treinamento e 20% para teste**, resultando em:

| Conjunto    | Quantidade de cursos |
| ----------- | -------------------: |
| Treinamento |                6.178 |
| Teste       |                1.545 |
| Total       |                7.723 |

Foi utilizado `random_state=42` para garantir reprodutibilidade.

O conjunto de teste permaneceu isolado durante toda a seleção dos modelos. Nenhum desempenho obtido no teste foi empregado para escolher algoritmos ou hiperparâmetros.

As transformações foram implementadas por meio de `Pipeline` e `ColumnTransformer` do Scikit-Learn. Isso garante que imputação, limites de IQR, padronização e One-Hot Encoding sejam ajustados somente com as observações disponíveis em cada conjunto de treinamento.

Durante a validação cruzada, todo o pré-processamento é reaprendido em cada `fold`, evitando que informações de uma parcela de validação sejam utilizadas antecipadamente no treinamento.

A mediana responsável pela criação do alvo também foi calculada exclusivamente no conjunto de treinamento. Esse cuidado é particularmente importante porque calcular o limiar utilizando o conjunto completo introduziria informação indireta do teste no processo de modelagem.

Os dados processados foram salvos em artefatos Parquet, incluindo as versões agregada, de treinamento e de teste, facilitando auditoria e reprodução dos experimentos.

---

# 2. Fase 2: Análise Exploratória e Engenharia de Modelagem

## 2.1 Gráficos Analíticos Essenciais

O modelo fornecido pelo professor limita esta seção a três gráficos. Foram selecionadas as visualizações que melhor representam a distribuição do desfecho, a comparação entre grupos e as associações multivariadas.

### Figura 1 - Distribuição da média da nota geral dos cursos

**Inserir:** `reports/figures/eda_01_histograma_nt_ger_media.png`

**Fonte:** elaborado pelo autor a partir dos Microdados do ENADE 2023.

A distribuição da média da nota geral dos cursos mostra que os **7.723 cursos elegíveis** apresentaram média global de aproximadamente **47,31 pontos**, mediana de **46,87** e desvio-padrão de **9,69**. O gráfico também apresenta o limiar de **46,8162**, obtido exclusivamente com os dados de treinamento e utilizado para construir a variável-alvo binária. A proximidade entre média e mediana sugere uma distribuição relativamente centrada, embora a dispersão demonstre diferenças relevantes entre os cursos. O limiar não deve ser interpretado como referência oficial de qualidade, mas como uma regra operacional criada para o experimento de classificação.

### Figura 2 - Distribuição do desempenho por modalidade

**Inserir:** `reports/figures/eda_02_boxplot_modalidade.png`

**Fonte:** elaborado pelo autor a partir dos Microdados do ENADE 2023.

A comparação descritiva entre modalidades revela diferenças nas distribuições observadas. Entre os **7.295 cursos presenciais**, a média de `NT_GER_MEDIA_CURSO` foi aproximadamente **47,73**, com mediana de **47,38**. Nos **428 cursos EaD**, a média observada foi aproximadamente **40,08**, com mediana de **39,86**. Entretanto, essa diferença não permite concluir que a modalidade seja causa do desempenho, principalmente porque os grupos apresentam tamanhos muito distintos e podem diferir em inúmeras características institucionais e socioeconômicas. O gráfico deve, portanto, ser interpretado como evidência exploratória que justifica análises multivariadas posteriores.

### Figura 3 - Heatmap das correlações de Spearman

**Inserir:** `reports/figures/eda_03_heatmap_correlacoes.png`

**Fonte:** elaborado pelo autor a partir dos Microdados do ENADE 2023.

A matriz de correlação de Spearman sintetiza associações monotônicas entre o desfecho e as variáveis numéricas agregadas mais relacionadas. Entre as maiores magnitudes identificadas destacaram-se `PROP_QE_I10_E`, com correlação de aproximadamente **-0,6173**, e `PROP_QE_I10_A`, com aproximadamente **0,5715**. Ambas derivam da variável `QE_I10`, associada à situação de trabalho declarada no questionário do estudante. Tais associações demonstram que o perfil agregado dos estudantes possui relação estatística com o desempenho dos cursos, porém não deve ser atribuído sentido causal aos coeficientes. Características socioeconômicas podem atuar em conjunto com diversos fatores não observados.

---

## 2.2 Hipóteses e principais achados exploratórios

A análise exploratória foi guiada por três hipóteses principais. A primeira questionou se a modalidade de ensino apresentava diferenças descritivas na distribuição da nota média dos cursos. O boxplot confirmou diferenças observacionais relevantes, mas insuficientes para inferência causal.

A segunda hipótese avaliou se características socioeconômicas agregadas poderiam apresentar associações com o desempenho. A matriz de correlação mostrou que algumas proporções associadas à situação de trabalho estavam entre as relações monotônicas de maior magnitude.

A terceira hipótese considerou que o desempenho não seria explicado adequadamente por uma única variável isolada. A combinação dos resultados exploratórios reforçou essa hipótese e justificou o uso de modelos multivariados.

Os achados foram empregados como suporte à modelagem, mantendo-se a premissa de que correlação e importância preditiva não representam causalidade.

---

## 2.3 Modelagem Preditiva

A modelagem foi estruturada como problema de classificação binária.

A **Regressão Logística regularizada** foi adotada como modelo baseline devido à simplicidade, interpretabilidade e capacidade de estabelecer uma referência clara de desempenho.

Como modelos avançados foram avaliados:

**Random Forest**, que combina múltiplas árvores de decisão por estratégia de ensemble; e **HistGradientBoostingClassifier**, baseado em boosting e otimizado por histogramas.

O XGBoost chegou a ser considerado, porém seu uso no ambiente macOS exigiria a instalação da biblioteca de sistema `libomp.dylib`. Como o desenvolvimento foi realizado em computador corporativo e o projeto deveria permanecer completamente isolado, optou-se por não modificar dependências globais do sistema. O `HistGradientBoostingClassifier` foi adotado como alternativa tecnicamente adequada e disponível no ambiente isolado do Scikit-Learn.

Para os modelos avançados foi utilizado `RandomizedSearchCV`, com avaliação de diferentes combinações de hiperparâmetros.

A validação empregou `StratifiedKFold` com **cinco folds**, embaralhamento habilitado e `random_state=42`. O critério principal para seleção foi o **F1-Score médio obtido durante a validação cruzada no treinamento**.

A escolha do F1-Score como métrica principal é adequada porque combina Precision e Recall em uma única medida, permitindo avaliar simultaneamente a capacidade de reduzir falsos alarmes e a capacidade de identificar corretamente as observações da classe de interesse. Accuracy e ROC-AUC foram utilizadas como métricas complementares.

### Tabela 1 - Comparação dos modelos

| Modelo               | F1 CV média ± DP | Accuracy Teste | Precision | Recall |   F1 Teste |    ROC-AUC |
| -------------------- | ---------------: | -------------: | --------: | -----: | ---------: | ---------: |
| Regressão Logística  |  0,8607 ± 0,0128 |     **0,8738** |    0,8626 | 0,8944 | **0,8782** | **0,9454** |
| HistGradientBoosting |  0,8541 ± 0,0119 |         0,8583 |    0,8584 | 0,8639 |     0,8611 |     0,9361 |
| Random Forest        |  0,8349 ± 0,0085 |         0,8311 |    0,8237 | 0,8499 |     0,8366 |     0,9201 |

**Fonte:** resultados computacionais do projeto.

A Regressão Logística apresentou o maior F1 médio durante a validação cruzada e, por essa razão, foi selecionada antes da avaliação final no teste.

No conjunto de teste, o modelo alcançou **Accuracy de 87,38%**, **Precision de 86,26%**, **Recall de 89,44%**, **F1-Score de 0,8782** e **ROC-AUC de 0,9454**.

O resultado demonstra que maior complexidade algorítmica não necessariamente conduz a melhor capacidade de generalização. Nesse conjunto específico de variáveis agregadas, a fronteira de decisão representada pela Regressão Logística regularizada apresentou desempenho superior aos ensembles avaliados.

O modelo final, juntamente com todo o pipeline de pré-processamento, foi salvo em:

**`models/melhor_modelo.joblib`**

Esse artefato foi posteriormente carregado e testado por inferência, confirmando sua integridade e reprodutibilidade.

---

## 2.4 Análise dos erros de classificação

A matriz de confusão do conjunto de teste apresentou:

| Resultado                | Quantidade |
| ------------------------ | ---------: |
| Verdadeiro Negativo (TN) |        647 |
| Falso Positivo (FP)      |        112 |
| Falso Negativo (FN)      |         83 |
| Verdadeiro Positivo (TP) |        703 |

Como a classe positiva representa cursos acima da mediana, um **falso positivo** corresponde a um curso classificado pelo modelo como acima da mediana quando, na realidade, pertence à classe inferior. Em uma aplicação de apoio institucional voltada à identificação de cursos que demandem acompanhamento, esse erro é particularmente relevante porque o curso poderia deixar de ser priorizado.

O **falso negativo**, por outro lado, ocorre quando um curso efetivamente acima da mediana é classificado como abaixo dela, podendo gerar uma análise ou intervenção institucional desnecessária.

Esses erros reforçam que o modelo não deve operar como mecanismo automático de punição, classificação institucional ou distribuição de recursos. As previsões devem funcionar como sinais de apoio submetidos à análise humana.

---

# 3. Fase 3: Visão de Negócio, ROI e Governança de Dados

## 3.1 Comunicação Visual - Dashboard

Foi desenvolvido o dashboard **ENADE Analytics**, utilizando Streamlit e Plotly, com foco em comunicação executiva dos resultados.

**Link público:** [INSERIR URL PÚBLICA DO DASHBOARD]

**Figura 4 - Dashboard ENADE Analytics em execução**

**Inserir aqui uma das capturas de tela do sistema em funcionamento.**

A solução apresenta uma interface orientada à exploração do desempenho dos cursos do ENADE 2023. Na barra lateral, o usuário pode aplicar filtros por região e modalidade. A área principal apresenta indicadores de cursos visualizados, média de `NT_GER`, F1-Score e ROC-AUC.

O dashboard foi estruturado em três blocos lógicos: **Visão Geral**, **Desempenho do Modelo** e **Explicabilidade e Governança**.

A aplicação possui seis visualizações interativas principais: distribuição das médias dos cursos, desempenho por região, comparação entre modelos, matriz de confusão, distribuição das probabilidades previstas e importância das variáveis.

Além dos gráficos, uma tabela permite consultar cursos individualmente no nível agregado, com filtros, mecanismo de busca e paginação. O sistema diferencia claramente os indicadores que variam conforme os filtros daqueles referentes ao conjunto fixo de teste, evitando interpretações equivocadas das métricas preditivas.

A arquitetura visual foi pensada para conduzir o usuário do cenário geral para a avaliação técnica do modelo e, por fim, para a análise de governança e limitações. Dessa maneira, o dashboard não apresenta somente números, mas estrutura uma narrativa de dados direcionada à tomada de decisão.

---

## 3.2 Retorno sobre o Investimento e ganho operacional estimado

Os Microdados do ENADE não possuem informações sobre custos operacionais de uma instituição, salários de analistas, tempo gasto atualmente na análise dos cursos ou benefício financeiro decorrente de uma intervenção. Consequentemente, seria metodologicamente inadequado apresentar um percentual financeiro de ROI como se fosse um resultado observado.

Apesar dessa limitação, é possível quantificar o **potencial ganho operacional de triagem** utilizando exclusivamente os resultados obtidos.

No conjunto de teste havia 1.545 cursos. Caso o objetivo institucional fosse priorizar a revisão aprofundada dos cursos classificados como abaixo da mediana, o modelo encaminharia **730 cursos** para análise prioritária, correspondentes a aproximadamente **47,25% do conjunto**.

Isso representa uma redução potencial de aproximadamente **52,75% no volume de cursos submetidos à primeira análise aprofundada**, comparativamente a uma estratégia na qual todos os 1.545 cursos fossem revisados com a mesma intensidade.

Entre os 759 cursos realmente pertencentes à classe abaixo da mediana, o modelo identificou corretamente 647, correspondendo a aproximadamente **85,24%** desse grupo.

Portanto, a principal proposta de valor não é automatizar decisões, mas utilizar o modelo como filtro inicial para concentrar recursos analíticos onde existe maior probabilidade de necessidade de acompanhamento.

No cenário real de implantação, o ROI financeiro poderá ser calculado quando a instituição fornecer dados de custo e benefício, empregando a expressão:

**ROI (%) = [(Benefício financeiro estimado − Custo total da solução) / Custo total da solução] × 100**

O custo total deverá incluir desenvolvimento, hospedagem, manutenção, atualização do modelo, treinamento dos usuários e tempo de especialistas. Os benefícios podem considerar redução de horas de análise manual, prevenção de perdas, melhor direcionamento de programas acadêmicos e economia decorrente da priorização de recursos.

Até que esses dados estejam disponíveis, o projeto reporta apenas ganho operacional mensurável e evita fabricar valores financeiros.

---

## 3.3 Riscos, Ética e Adequação à LGPD

A análise dos Microdados do ENADE exige atenção especial à privacidade, porque o conjunto contém características que podem ser sensíveis quando associadas a pessoas, como sexo, renda familiar, escola de origem e participação em políticas de ação afirmativa.

O projeto preservou deliberadamente a estrutura de proteção disponibilizada pelo INEP. Os diferentes arquivos não foram unidos com a intenção de reconstruir perfis individuais. As informações foram agregadas separadamente por curso e somente depois integradas.

A unidade de inferência do modelo é, portanto, o **curso**, e não o estudante.

Mesmo em nível agregado, variáveis socioeconômicas devem ser utilizadas com cautela. Uma associação entre determinada característica e desempenho não autoriza interpretações causais ou decisões discriminatórias.

O sistema não deve ser empregado para restringir direitos, punir cursos, excluir estudantes, realizar ranking oficial de instituições ou substituir avaliações conduzidas por especialistas.

Em eventual implantação, recomenda-se revisão humana obrigatória, controle de acesso, registro de previsões, auditoria periódica por grupos e regiões, monitoramento da estabilidade das variáveis e documentação das decisões apoiadas pelo modelo.

Também deve ser considerada a possibilidade de `data drift`. Como o projeto utiliza apenas a edição 2023 do ENADE, mudanças curriculares, regulatórias, demográficas ou comportamentais podem fazer com que o padrão aprendido deixe de representar adequadamente edições futuras.

Por isso, qualquer utilização contínua deverá incluir validações temporais e procedimentos de retreinamento.

---

# 4. Cronograma de Execução e Próximos Passos

Por se tratar de um projeto desenvolvido individualmente, todas as fases tiveram o mesmo responsável. O cronograma abaixo apresenta o planejamento lógico adotado.

| Fase | Atividade Principal                                                            | Responsável      | Período Estimado | Status    |
| ---- | ------------------------------------------------------------------------------ | ---------------- | ---------------- | --------- |
| 1    | Aquisição, auditoria, limpeza, engenharia de atributos e split de treino/teste | Autor do projeto | Semana 1         | Concluído |
| 2    | Análise exploratória, treinamento, tuning, validação e seleção do modelo       | Autor do projeto | Semana 2         | Concluído |
| 3    | Construção do dashboard, análise de negócio, riscos, LGPD e relatório final    | Autor do projeto | Semana 3         | Concluído |

Caso seja necessário utilizar datas de calendário, substituir "Semana 1", "Semana 2" e "Semana 3" pelas datas reais de desenvolvimento antes da entrega.

## 4.1 Próximos passos

Como evolução do projeto, recomenda-se inicialmente incorporar outras edições do ENADE para avaliar a capacidade de generalização temporal.

Outra possibilidade é transformar o problema em regressão, utilizando diretamente `NT_GER_MEDIA_CURSO` como variável contínua. Essa abordagem permitiria estimar a nota média esperada, em vez de apenas classificar acima ou abaixo de um limiar.

Também se recomenda investigar intervalos de incerteza ponderados pelo número de estudantes do curso, visto que médias calculadas a partir de amostras maiores tendem a apresentar maior estabilidade.

Uma etapa futura de explicabilidade pode aprofundar a interpretação do modelo por meio de métodos de IA Explicável, como SHAP ou LIME, desde que sua utilização seja compatível com o pipeline adotado.

No contexto operacional, recomenda-se ainda criar mecanismo de monitoramento do desempenho ao longo do tempo, com alertas para mudanças na distribuição dos dados e eventual necessidade de retreinamento.

---

# 5. Gestão de Riscos Aplicada ao Projeto

## 5.1 Introdução

Projetos de Inteligência Artificial e Ciência de Dados apresentam natureza experimental e probabilística. Diferentemente de um sistema tradicional baseado exclusivamente em regras determinísticas, um modelo preditivo pode apresentar variação de desempenho ao ser exposto a novos dados.

A gestão de riscos deste projeto considera princípios presentes em boas práticas de gerenciamento de projetos, gestão de riscos e governança de Inteligência Artificial, incluindo PMBOK, ISO 31000, CRISP-DM e NIST AI Risk Management Framework.

Os riscos foram analisados nas dimensões de dados, técnica, operacional, legal e de utilização institucional.

---

## 5.2 Riscos de dados

Um primeiro risco está associado à qualidade dos dados fornecidos pelos próprios participantes dos questionários. Algumas variáveis possuem valores ausentes, respostas não aplicáveis ou inconsistências.

Como mitigação, foram aplicadas regras explícitas de tratamento, imputação e registro das inconsistências.

Outro risco está relacionado à impossibilidade de vinculação individual entre os arquivos. Essa restrição reduz a granularidade das análises, porém também atua como mecanismo de proteção à privacidade. O projeto optou por preservá-la e trabalhar exclusivamente em nível agregado.

Existe ainda risco de instabilidade estatística em cursos com poucos participantes. Para reduzir esse problema, foram incluídos apenas cursos com pelo menos dez notas válidas.

---

## 5.3 Riscos de modelagem e técnicos

O principal risco técnico é o `overfitting`, caracterizado por desempenho elevado durante o treinamento e degradação em observações desconhecidas.

A mitigação incluiu separação prévia do conjunto de teste, validação cruzada estratificada em cinco folds, regularização e comparação entre diferentes algoritmos.

Outro risco relevante é o `data leakage`. Para preveni-lo, o limiar da variável-alvo foi calculado somente no treinamento e todo o pré-processamento foi mantido dentro de `Pipeline` e `ColumnTransformer`.

A escolha final também não utilizou as métricas de teste. A Regressão Logística foi selecionada pelo maior F1 médio de validação cruzada e somente depois foi avaliada no conjunto final.

---

## 5.4 Riscos operacionais

A utilização de dados de uma única edição cria risco de degradação temporal. O comportamento observado em 2023 pode não se repetir em futuras aplicações.

A mitigação recomendada consiste em monitorar indicadores de desempenho, distribuição das variáveis e mudanças na população analisada.

Em caso de alteração significativa, novas edições devem ser incorporadas e o modelo submetido a novo treinamento e validação.

Há também risco relacionado a alterações no formato dos dados oficiais do INEP. A arquitetura deve, portanto, preservar documentação e testes de ingestão para permitir adaptação futura.

---

## 5.5 Riscos de negócio e adoção

Um modelo com bom desempenho estatístico pode gerar pouco valor caso seja utilizado para uma decisão inadequada.

Neste projeto, o modelo deve atuar como ferramenta de apoio à análise e priorização, e não como instrumento automático de avaliação oficial.

A ausência de transparência também pode reduzir a confiança dos usuários. A escolha da Regressão Logística como modelo final favorece a interpretabilidade, visto que seus coeficientes podem ser examinados para compreender a direção e magnitude relativa das associações preditivas.

Ainda assim, nenhuma importância de variável deve ser confundida com efeito causal.

---

## 5.6 Matriz de Riscos

| Categoria  | Descrição do risco                                                                      | Probabilidade | Impacto    | Ação mitigadora                                                                                |
| ---------- | --------------------------------------------------------------------------------------- | ------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| Dados      | Questionários com valores ausentes, inconsistentes ou autorrelatados                    | Média         | Alto       | Validação, imputação documentada, indicadores de inconsistência e auditoria periódica          |
| Dados/LGPD | Tentativa de reconstruir informação individual ou uso inadequado de atributos sensíveis | Baixa         | Muito Alto | Manter agregação por curso, controle de acesso, minimização de dados e revisão de conformidade |
| Técnico    | Data leakage durante preparação ou criação do alvo                                      | Baixa         | Muito Alto | Pipeline/ColumnTransformer, limiar calculado somente no treino e teste isolado                 |
| Técnico    | Overfitting e perda de capacidade de generalização                                      | Média         | Alto       | 5-fold CV, regularização, comparação de modelos e conjunto de teste não utilizado na seleção   |
| Operação   | Data drift entre edições do ENADE                                                       | Alta          | Médio/Alto | Monitoramento temporal, validação com novas edições e retreinamento                            |
| Negócio    | Falso positivo deixar de priorizar curso que realmente apresentou desempenho inferior   | Média         | Alto       | Revisão humana e uso combinado com outros indicadores institucionais                           |
| Negócio    | Falso negativo gerar análise ou intervenção desnecessária                               | Média         | Médio      | Confirmação por especialista antes de qualquer ação                                            |
| Adoção     | Usuários interpretarem associação estatística como causalidade                          | Média         | Alto       | Dashboard com ressalvas, documentação, explicabilidade e capacitação dos usuários              |

---

# 6. Discussão dos Resultados

O projeto demonstrou a viabilidade de aplicação de técnicas de Machine Learning sobre dados educacionais públicos em nível agregado.

Um dos resultados mais relevantes foi a superioridade da Regressão Logística em comparação aos modelos de maior complexidade. Apesar de Random Forest e HistGradientBoosting possuírem capacidade de modelar relações não lineares, ambos apresentaram F1 inferior no cenário avaliado.

Esse resultado reforça um princípio importante da Ciência de Dados: a complexidade do algoritmo deve ser justificada pelo ganho de desempenho e não utilizada como finalidade em si mesma.

O ROC-AUC de **0,9454** indica forte capacidade de discriminação entre as duas classes operacionais. O Recall de **0,8944** demonstra que o modelo identificou grande parte dos cursos pertencentes à classe positiva.

Entretanto, as métricas não significam que o modelo seja capaz de medir oficialmente a qualidade de um curso ou explicar causalmente o desempenho no ENADE.

As variáveis são predominantemente agregadas e muitas delas derivam de questionários autorrelatados. Além disso, a análise considera somente a edição 2023.

A exclusão de cursos com menos de dez resultados melhora a estabilidade estatística, mas limita a abrangência da análise e pode deixar de representar cursos pequenos.

As diferenças observadas entre modalidades, regiões ou perfis socioeconômicos devem ser tratadas como descritivas. Há fatores institucionais e contextuais não capturados pela base que podem influenciar os resultados.

Em termos de confiabilidade, a separação rigorosa entre treino e teste, o uso de validação cruzada, a manutenção do pré-processamento dentro do pipeline e a utilização de seed fixa aumentam a reprodutibilidade do estudo.

Todos os notebooks foram executados sem erros salvos e o artefato final foi submetido a teste de carregamento e inferência.

---

# 7. Conclusão

Este trabalho desenvolveu um pipeline completo de Ciência de Dados aplicado aos Microdados do ENADE 2023, abrangendo aquisição, preparação, análise exploratória, modelagem preditiva, visualização e discussão crítica.

A unidade de análise no nível de curso permitiu explorar diferentes fontes de informação sem romper as salvaguardas de privacidade existentes nos arquivos oficiais.

Após o processamento, foram obtidos 7.723 cursos elegíveis, divididos entre 6.178 observações para treinamento e 1.545 para teste.

A comparação entre Regressão Logística, HistGradientBoosting e Random Forest indicou a Regressão Logística como melhor modelo segundo o F1 médio da validação cruzada.

No teste, o modelo final obteve Accuracy de **0,8738**, Precision de **0,8626**, Recall de **0,8944**, F1-Score de **0,8782** e ROC-AUC de **0,9454**.

Os resultados demonstram que um modelo relativamente simples e interpretável pode apresentar desempenho superior a algoritmos mais complexos quando aplicado a uma representação agregada adequada.

O dashboard desenvolvido amplia a entrega de valor ao transformar resultados técnicos em visualizações navegáveis e compreensíveis, permitindo filtros, consulta dos cursos, comparação entre modelos e análise dos principais indicadores.

Do ponto de vista institucional, a aplicação possui potencial para apoiar a priorização de análises acadêmicas. Com base no conjunto de teste, uma estratégia de triagem baseada na classe prevista como abaixo da mediana poderia reduzir em cerca de 52,75% o volume inicialmente submetido a análise aprofundada, preservando a identificação de aproximadamente 85,24% dos cursos efetivamente pertencentes àquela classe.

Esse ganho deve ser interpretado como eficiência operacional potencial, e não como ROI financeiro comprovado.

A adoção prática exige validação humana, monitoramento contínuo, respeito à LGPD e cuidado para que associações estatísticas não sejam utilizadas como justificativa para decisões discriminatórias ou avaliações oficiais.

Como evolução, recomenda-se incorporar novas edições do ENADE, avaliar modelos de regressão do desempenho contínuo, aprofundar técnicas de explicabilidade e criar processos de monitoramento de `data drift`.

Dessa forma, o projeto materializa o princípio **“Do Dado ao Valor”**, demonstrando que o valor da Inteligência Artificial não está apenas na construção de um algoritmo, mas na capacidade de transformar dados em evidências úteis, auditáveis, responsáveis e efetivamente aplicáveis ao processo decisório.

---

# Referências

BRASIL. **Lei nº 13.709, de 14 de agosto de 2018**. Lei Geral de Proteção de Dados Pessoais (LGPD). Brasília, DF: Presidência da República, 2018.

BRUCE, Peter; BRUCE, Andrew; GEDECK, Peter. _Practical Statistics for Data Scientists: 50+ Essential Concepts Using R and Python_. 2. ed. Sebastopol: O'Reilly Media, 2020.

CHAPMAN, Pete et al. _CRISP-DM 1.0: Step-by-step data mining guide_. SPSS, 2000.

GÉRON, Aurélien. _Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow_. 3. ed. Sebastopol: O'Reilly Media, 2022.

HASTIE, Trevor; TIBSHIRANI, Robert; FRIEDMAN, Jerome. _The Elements of Statistical Learning: Data Mining, Inference, and Prediction_. 2. ed. New York: Springer, 2009.

INEP - INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA. _Microdados do Exame Nacional de Desempenho dos Estudantes - ENADE 2023_. Brasília, DF: INEP.

INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. _ISO 31000:2018 - Risk management: Guidelines_. Geneva: ISO, 2018.

NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. _Artificial Intelligence Risk Management Framework (AI RMF 1.0)_. Gaithersburg: NIST, 2023.

PEDREGOSA, Fabian et al. Scikit-learn: Machine Learning in Python. _Journal of Machine Learning Research_, v. 12, p. 2825-2830, 2011.

PROJECT MANAGEMENT INSTITUTE. _A Guide to the Project Management Body of Knowledge (PMBOK Guide) and The Standard for Project Management_. 7. ed. Newtown Square: PMI, 2021.

---

# Artefatos técnicos complementares da entrega

O repositório do projeto deve acompanhar o relatório e contém os seguintes artefatos principais:

`notebooks/01_aquisicao.ipynb` - aquisição e auditoria inicial dos dados.

`notebooks/02_preparacao.ipynb` - preparação, agregação e pré-processamento.

`notebooks/03_eda.ipynb` - análise exploratória e geração dos gráficos.

`notebooks/04_modelagem.ipynb` - treinamento, validação e comparação dos modelos.

`models/melhor_modelo.joblib` - pipeline e modelo final selecionado.

`reports/tables/metricas_modelos.csv` - resultados comparativos dos algoritmos.

`reports/figures/` - gráficos produzidos durante EDA e modelagem.

`app/dashboard.py` - aplicação Streamlit/Plotly.

`requirements.txt` - dependências e versões necessárias à reprodução.

`README.md` - instruções completas de instalação e execução.

O projeto utiliza `random_state=42` em todas as etapas estocásticas relevantes e mantém as transformações de pré-processamento integradas ao pipeline do modelo.
