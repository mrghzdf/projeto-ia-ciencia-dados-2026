"""Gera tabelas, gráficos PNG e insights reproduzíveis da EDA."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import FIGURES_DIR, PROCESSED_DIR, TABLES_DIR
from src.preparation import TARGET_BINARY, TARGET_SCORE

SNS_STYLE = "whitegrid"


def _save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / name, dpi=160, bbox_inches="tight")
    plt.close()


def generate_eda_artifacts() -> dict:
    """Produz EDA a partir dos splits, sem alterar dados ou modelos."""
    train = pd.read_parquet(PROCESSED_DIR / "train_cursos.parquet")
    test = pd.read_parquet(PROCESSED_DIR / "test_cursos.parquet")
    data = pd.concat([train.assign(CONJUNTO="treino"), test.assign(CONJUNTO="teste")], ignore_index=True)
    metadata = json.loads((PROCESSED_DIR / "metadata_preparacao.json").read_text(encoding="utf-8"))
    threshold = metadata["limiar_mediana_aprendido_no_treino"]

    sns.set_theme(style=SNS_STYLE, context="notebook")
    summary = data.describe(include="all").transpose()
    summary.to_csv(TABLES_DIR / "estatisticas_descritivas.csv", encoding="utf-8-sig")
    missing = data.isna().mean().sort_values(ascending=False).rename("proporcao_nulos")
    missing.to_csv(TABLES_DIR / "proporcao_nulos.csv", encoding="utf-8-sig")

    # Correlações usam somente preditores elegíveis; notas auxiliares e informações
    # do desfecho permanecem fora para não criar uma associação tautológica.
    eligible_numeric = [name for name in metadata["numeric_features"] if name in data.columns]
    correlation_frame = data[[TARGET_SCORE] + eligible_numeric]
    correlations = correlation_frame.corr(method="spearman")[TARGET_SCORE].drop(TARGET_SCORE).sort_values(key=abs, ascending=False)
    correlations.rename("spearman_com_nt_ger_media").to_csv(
        TABLES_DIR / "correlacoes_spearman_target.csv", encoding="utf-8-sig"
    )

    # Gráficos que vão pro relatório e pro dashboard
    plt.figure(figsize=(9, 5))
    sns.histplot(data=data, x=TARGET_SCORE, bins=35, kde=True, color="#2F6B8A")
    plt.axvline(threshold, color="#C44E52", linestyle="--", label=f"Mediana do treino = {threshold:.2f}")
    plt.title("Distribuição da nota média dos cursos")
    plt.xlabel("Média de NT_GER por curso")
    plt.ylabel("Quantidade de cursos")
    plt.legend()
    _save("eda_01_histograma_nt_ger_media.png")

    # 2. Boxplot por modalidade, mantendo códigos oficiais no eixo.
    plot_data = data.assign(
        MODALIDADE=data["CO_MODALIDADE"].astype(str).map({"0": "EaD", "1": "Presencial"}).fillna("Outro")
    )
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=plot_data, x="MODALIDADE", y=TARGET_SCORE, color="#4C9F70")
    plt.title("Nota média do curso por modalidade")
    plt.xlabel("Modalidade")
    plt.ylabel("Média de NT_GER por curso")
    _save("eda_02_boxplot_modalidade.png")

    # 3. Heatmap das variáveis com maior correlação absoluta com o desfecho.
    top_features = correlations.index[:10].tolist()
    heatmap_columns = [TARGET_SCORE] + top_features
    plt.figure(figsize=(11, 8))
    sns.heatmap(data[heatmap_columns].corr(method="spearman"), cmap="vlag", center=0, annot=False)
    plt.title("Heatmap de correlação de Spearman (variáveis mais associadas ao alvo)")
    _save("eda_03_heatmap_correlacoes.png")

    # 4. Distribuição das classes derivadas pelo limiar do treino.
    plt.figure(figsize=(7, 5))
    counts = data[TARGET_BINARY].value_counts().sort_index()
    sns.barplot(x=["Até a mediana", "Acima da mediana"], y=counts.values, color="#8172B2")
    plt.title("Distribuição do alvo de classificação")
    plt.xlabel("Classe")
    plt.ylabel("Quantidade de cursos")
    _save("eda_04_distribuicao_classes.png")

    # 5. Nulos: mostra apenas as colunas com algum valor ausente.
    missing_nonzero = missing[missing > 0].head(20).sort_values()
    plt.figure(figsize=(9, max(4, len(missing_nonzero) * 0.28)))
    sns.barplot(x=missing_nonzero.values * 100, y=missing_nonzero.index, color="#DD8452")
    plt.title("Maiores proporções de valores ausentes")
    plt.xlabel("Valores ausentes (%)")
    plt.ylabel("Variável")
    _save("eda_05_nulos.png")

    # 6. Boxplots de atributos numéricos antes do clipping feito no Pipeline.
    box_columns = ["N_INSCRITOS", "IDADE_MEDIA", "AVALIACAO_PROCESSO_MEDIA", "ANOS_DESDE_INICIO_GRAD_MEDIANA"]
    standardized = data[box_columns].copy()
    standardized = (standardized - standardized.median()) / standardized.std(ddof=0)
    long = standardized.melt(var_name="Variável", value_name="Valor padronizado apenas para o gráfico")
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=long, x="Variável", y="Valor padronizado apenas para o gráfico", color="#64B5CD")
    plt.xticks(rotation=20, ha="right")
    plt.title("Boxplots de variáveis numéricas agregadas (antes do tratamento no Pipeline)")
    _save("eda_06_boxplots_numericos.png")

    # 7. Relação entre tamanho da turma e nota, em escala log no eixo x.
    plt.figure(figsize=(9, 5))
    sns.scatterplot(data=data, x="N_RESULTADOS_VALIDOS", y=TARGET_SCORE, alpha=0.35, s=22, color="#2F6B8A")
    plt.xscale("log")
    plt.title("Nota média e quantidade de resultados válidos por curso")
    plt.xlabel("Resultados válidos (escala log)")
    plt.ylabel("Média de NT_GER por curso")
    _save("eda_07_dispersao_tamanho_nota.png")

    top_corr = correlations.head(5)
    insights = {
        "n_cursos": len(data),
        "media_target": float(data[TARGET_SCORE].mean()),
        "mediana_target": float(data[TARGET_SCORE].median()),
        "desvio_target": float(data[TARGET_SCORE].std()),
        "limiar_target_treino": threshold,
        "prevalencia_classe_1": float(data[TARGET_BINARY].mean()),
        "maior_taxa_nulos": float(missing.max()),
        "top_correlacoes_spearman": {key: float(value) for key, value in top_corr.items()},
    }
    (TABLES_DIR / "insights_eda.json").write_text(
        json.dumps(insights, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return insights
