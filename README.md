# Projeto ABP - Do Dado ao Valor

## Aplicacao de Machine Learning para Analise Preditiva do Desempenho dos Cursos no ENADE 2023

**Curso:** Pos-Graduacao em Ciencia de Dados e Inteligencia Artificial
**Disciplina:** Inteligencia Artificial para Ciencia de Dados -- Turma B -- 0726
**Dataset:** Microdados do ENADE 2023
**Fonte:** Instituto Nacional de Estudos e Pesquisas Educacionais Anisio Teixeira -- INEP
**Modalidade do dado:** Tabular
**Link do dataset:** <https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enade>

---

## Descricao do projeto

Este projeto implementa um pipeline completo de Ciencia de Dados aplicado aos Microdados do ENADE 2023, cobrindo o fluxo **Aquisicao -> Preparacao -> EDA -> Modelagem -> Visualizacao**.

O objetivo e desenvolver e avaliar um modelo de Machine Learning capaz de classificar cursos de ensino superior segundo a probabilidade de apresentarem media da nota geral (`NT_GER`) acima do limiar definido exclusivamente com os dados de treinamento.

A unidade de analise e o **curso** (identificado por `CO_CURSO`), preservando a estrutura de protecao LGPD dos microdados do INEP. Nenhum perfil individual de estudante e reconstruido.

## Resultado tecnico

| Modelo | F1 CV (media +/- DP) | Accuracy | Precision | Recall | F1 Teste | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Regressao Logistica | 0,8607 +/- 0,0128 | 0,8738 | 0,8626 | 0,8944 | **0,8782** | **0,9454** |
| HistGradientBoosting | 0,8541 +/- 0,0119 | 0,8583 | 0,8584 | 0,8639 | 0,8611 | 0,9361 |
| Random Forest | 0,8349 +/- 0,0085 | 0,8311 | 0,8237 | 0,8499 | 0,8366 | 0,9201 |

- **Melhor modelo:** Regressao Logistica (selecionado pelo maior F1 medio em validacao cruzada estratificada de 5 folds).
- **Pipeline completo salvo em:** `models/melhor_modelo.joblib`
- **Split:** 80/20 com `random_state=42` (6.178 cursos no treino, 1.545 no teste).

## Estrutura do projeto

```text
projeto-ia-ciencia-dados-2026/
|
|-- app/                        Dashboard Streamlit/Plotly
|   +-- dashboard.py
|
|-- data/
|   |-- interim/                Amostra e tabela agregada por curso
|   +-- processed/              Splits treino/teste e metadados
|
|-- docs/                       Documentacao, decisoes e rastreabilidade
|   |-- decisao_alvo_lgpd_e_limitacoes.md
|   |-- dicionario_principais_colunas.md
|   |-- inspecao_dataset.md
|   |-- resumo_resultados_tecnicos.md
|   +-- relatorio_academico_rascunho.md
|
|-- models/                     Melhor pipeline em joblib e metadados
|   |-- melhor_modelo.joblib
|   +-- metadata_modelo.json
|
|-- notebooks/                  Notebooks do fluxo pedagogico
|   |-- 01_aquisicao.ipynb
|   |-- 02_preparacao.ipynb
|   |-- 03_eda.ipynb
|   +-- 04_modelagem.ipynb
|
|-- reports/
|   |-- figures/                Graficos PNG (EDA e modelagem)
|   +-- tables/                 Metricas, predicoes, importancias e inventario
|
|-- scripts/                    Execucao dos notebooks e smoke test
|   |-- run_notebooks.py
|   +-- smoke_test.py
|
|-- src/                        Codigo reutilizavel
|   |-- __init__.py
|   |-- config.py               Caminhos e constantes centrais
|   |-- data.py                 Leitura, auditoria e agregacao LGPD-safe
|   |-- eda.py                  Graficos e insights da analise exploratoria
|   |-- modeling.py             Pipeline, avaliacao e interpretacao
|   |-- preparation.py          Split reproduzivel e alvo de classificacao
|   |-- training.py             Treinamento, tuning e persistencia
|   +-- transformers.py         Transformador IQRClipper customizado
|
|-- .streamlit/config.toml      Tema do dashboard
|-- .gitignore
|-- preparar_ambiente.sh        Cria o ambiente virtual e instala dependencias
|-- requirements.txt            Dependencias com versoes fixas
|-- rodar_dashboard.sh          Abre o dashboard Streamlit
+-- rodar_pipeline.sh           Executa o fluxo completo de notebooks
```

## Execucao reproduzivel

Requer **Python 3.13**. A instalacao permanece na pasta `.venv` deste projeto.

### Execucao simplificada (macOS)

O ambiente e os artefatos ja estao preparados. Para abrir diretamente o dashboard:

```bash
./rodar_dashboard.sh
```

Caso a `.venv` tenha sido removida, reconstrua-a primeiro:

```bash
./preparar_ambiente.sh
./rodar_dashboard.sh
```

Para refazer todo o processamento e treinamento:

```bash
./rodar_pipeline.sh
./rodar_dashboard.sh
```

Use `Ctrl+C` no terminal para encerrar o dashboard.

### Execucao manual

```bash
python3 -m venv .venv
PIP_CACHE_DIR="$PWD/.pip-cache" .venv/bin/python -m pip install -r requirements.txt
PYTHONPATH="$PWD" .venv/bin/python scripts/run_notebooks.py
PYTHONPATH="$PWD" .venv/bin/python scripts/smoke_test.py
```

### Dashboard

Apos executar os notebooks:

```bash
PYTHONPATH="$PWD" .venv/bin/python -m streamlit run app/dashboard.py
```

## Documentacao tecnica

| Documento | Conteudo |
|---|---|
| [Resultados tecnicos](docs/resumo_resultados_tecnicos.md) | Metricas, protocolo e modelo selecionado |
| [Decisao do alvo e LGPD](docs/decisao_alvo_lgpd_e_limitacoes.md) | Justificativa do alvo, leakage, limitacoes |
| [Inspecao do dataset](docs/inspecao_dataset.md) | Origem, formato e regras de importacao |
| [Dicionario de colunas](docs/dicionario_principais_colunas.md) | Variaveis originais e engenheiradas |

## Observacoes

- O alvo binario nao e uma nota oficial de aprovacao ou Conceito Enade.
- O modelo e exploratorio e agregado; nao deve embasar decisoes individuais ou causais.
- O XGBoost nao foi utilizado porque requer `libomp.dylib` global neste macOS. O `HistGradientBoostingClassifier` foi adotado como alternativa de boosting reproduzivel.
- Confira os termos atuais do INEP na [pagina oficial dos Microdados do Enade](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enade) antes de redistribuir derivados.
