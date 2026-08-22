"""Cria o split reproduzível e o alvo de classificação sem vazamento."""

from __future__ import annotations

import json

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import INTERIM_DIR, PROCESSED_DIR, RANDOM_STATE, TEST_SIZE
from src.data import build_course_dataset, feature_columns

MIN_VALID_RESULTS = 10
TARGET_SCORE = "NT_GER_MEDIA_CURSO"
TARGET_BINARY = "TARGET_ACIMA_MEDIANA_TREINO"


def prepare_and_split(save: bool = True):
    """Filtra cursos com suporte mínimo, divide e deriva o alvo pelo treino.

    A mediana não usa o teste. O alvo significa apenas "acima da mediana do
    treino"; não é nota de aprovação, conceito Enade ou juízo de qualidade oficial.
    """
    interim_path = INTERIM_DIR / "enade_2023_cursos_agregado.parquet"
    if interim_path.exists():
        dataset = pd.read_parquet(interim_path)
    else:
        dataset, _ = build_course_dataset(save=True)

    dataset = dataset.loc[dataset["N_RESULTADOS_VALIDOS"] >= MIN_VALID_RESULTS].copy()
    dataset = dataset.drop_duplicates(subset=["CO_CURSO"]).reset_index(drop=True)

    train, test = train_test_split(
        dataset,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        shuffle=True,
    )
    threshold = float(train[TARGET_SCORE].median())
    train[TARGET_BINARY] = (train[TARGET_SCORE] > threshold).astype("int8")
    test[TARGET_BINARY] = (test[TARGET_SCORE] > threshold).astype("int8")

    numeric_features, categorical_features = feature_columns(train)
    # Códigos são categorias nominais, não grandezas numéricas ordinais.
    for column in categorical_features:
        train[column] = train[column].astype("string")
        test[column] = test[column].astype("string")

    metadata = {
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "min_resultados_validos_por_curso": MIN_VALID_RESULTS,
        "limiar_mediana_aprendido_no_treino": threshold,
        "target_score": TARGET_SCORE,
        "target_binario": TARGET_BINARY,
        "descricao_target": "1 se a média NT_GER do curso excede a mediana aprendida no treino; 0 caso contrário",
        "nao_eh": "nota de aprovação ou conceito oficial do INEP",
        "n_train": len(train),
        "n_test": len(test),
        "prevalencia_train": float(train[TARGET_BINARY].mean()),
        "prevalencia_test": float(test[TARGET_BINARY].mean()),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
    }
    if save:
        train.to_parquet(PROCESSED_DIR / "train_cursos.parquet", index=False)
        test.to_parquet(PROCESSED_DIR / "test_cursos.parquet", index=False)
        (PROCESSED_DIR / "metadata_preparacao.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return train, test, metadata

