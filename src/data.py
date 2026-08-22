"""Leitura, auditoria e agregação LGPD-safe dos microdados do ENADE 2023."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import ANO_ENADE, INTERIM_DIR, RAW_DATA_DIR


# Questões de perfil selecionadas por relevância educacional e parcimônia.
QUESTION_FILES = {
    14: "QE_I08",  # renda familiar
    16: "QE_I10",  # situação de trabalho
    21: "QE_I15",  # ação afirmativa
    23: "QE_I17",  # tipo de escola no ensino médio
    27: "QE_I21",  # familiar com ensino superior
    28: "QE_I22",  # leitura extraclasse
    29: "QE_I23",  # horas de estudo
    31: "QE_I25",  # motivo de escolha do curso
    32: "QE_I26",  # motivo de escolha da IES
}

CATEGORICAL_FEATURES = [
    "CO_CATEGAD",
    "CO_ORGACAD",
    "CO_GRUPO",
    "CO_MODALIDADE",
    "CO_UF_CURSO",
    "CO_REGIAO_CURSO",
]

NON_FEATURE_COLUMNS = {
    "CO_CURSO",
    "CO_IES",
    "CO_MUNIC_CURSO",
    "NU_ANO",
    "NT_GER_MEDIA_CURSO",
    "NT_GER_MEDIANA_CURSO",
    "NT_GER_DP_CURSO",
    "N_RESULTADOS_VALIDOS",
    "TX_PRESENCA_VALIDA",
    "TARGET_ACIMA_MEDIANA_TREINO",
}


def raw_path(file_number: int) -> Path:
    """Retorna o caminho de um dos 32 arquivos de dados."""
    return RAW_DATA_DIR / f"microdados2023_arq{file_number}.txt"


def read_raw(file_number: int, usecols: list[str] | None = None) -> pd.DataFrame:
    """Lê arquivo oficial com regras do manual: ';', decimal '.' e '.' como nulo."""
    return pd.read_csv(
        raw_path(file_number),
        sep=";",
        decimal=".",
        na_values=["."],
        usecols=usecols,
        low_memory=False,
    )


def _mode_or_nan(series: pd.Series):
    modes = series.dropna().mode()
    return modes.iloc[0] if not modes.empty else np.nan


def _validate_course_constants(df: pd.DataFrame, columns: list[str]) -> dict[str, int]:
    """Conta cursos com mais de um valor por atributo antes de escolher a moda."""
    return {
        col: int((df.groupby("CO_CURSO")[col].nunique(dropna=True) > 1).sum())
        for col in columns
    }


def _aggregate_base() -> tuple[pd.DataFrame, dict]:
    raw = read_raw(1)
    attributes = [
        "NU_ANO",
        "CO_IES",
        "CO_CATEGAD",
        "CO_ORGACAD",
        "CO_GRUPO",
        "CO_MODALIDADE",
        "CO_MUNIC_CURSO",
        "CO_UF_CURSO",
        "CO_REGIAO_CURSO",
    ]
    conflicts = _validate_course_constants(raw, attributes)
    grouped = raw.groupby("CO_CURSO", as_index=False).agg(
        **{col: (col, _mode_or_nan) for col in attributes},
        N_INSCRITOS=("CO_CURSO", "size"),
    )
    return grouped, {"conflitos_atributos_curso": conflicts}


def _aggregate_outcome() -> pd.DataFrame:
    raw = read_raw(3, ["CO_CURSO", "TP_PRES", "NT_GER"])
    raw["PRESENCA_VALIDA"] = (raw["TP_PRES"] == 555).astype(float)
    valid = raw.loc[(raw["TP_PRES"] == 555) & raw["NT_GER"].notna()].copy()
    scores = valid.groupby("CO_CURSO")["NT_GER"].agg(
        NT_GER_MEDIA_CURSO="mean",
        NT_GER_MEDIANA_CURSO="median",
        NT_GER_DP_CURSO="std",
        N_RESULTADOS_VALIDOS="size",
    )
    attendance = raw.groupby("CO_CURSO")["PRESENCA_VALIDA"].mean().rename("TX_PRESENCA_VALIDA")
    return scores.join(attendance).reset_index()


def _aggregate_academic() -> pd.DataFrame:
    raw = read_raw(2)

    # O dicionário registra anos digitados incorretamente (ex.: 1016 e 2914).
    # Em vez de capar anos impossíveis, eles são convertidos em nulos para imputação posterior.
    for col in ("ANO_FIM_EM", "ANO_IN_GRAD"):
        raw[f"{col}_INVALIDO"] = (~raw[col].between(1950, ANO_ENADE)).astype(float)
        raw[col] = raw[col].where(raw[col].between(1950, ANO_ENADE))

    raw["ANOS_DESDE_FIM_EM"] = ANO_ENADE - raw["ANO_FIM_EM"]
    raw["ANOS_DESDE_INICIO_GRAD"] = ANO_ENADE - raw["ANO_IN_GRAD"]
    aggregated = raw.groupby("CO_CURSO").agg(
        ANOS_DESDE_FIM_EM_MEDIANA=("ANOS_DESDE_FIM_EM", "median"),
        ANOS_DESDE_INICIO_GRAD_MEDIANA=("ANOS_DESDE_INICIO_GRAD", "median"),
        TX_ANO_FIM_EM_INVALIDO=("ANO_FIM_EM_INVALIDO", "mean"),
        TX_ANO_IN_GRAD_INVALIDO=("ANO_IN_GRAD_INVALIDO", "mean"),
    )
    turns = pd.crosstab(raw["CO_CURSO"], raw["CO_TURNO_GRADUACAO"], normalize="index")
    turns.columns = [f"PROP_TURNO_{int(value)}" for value in turns.columns]
    return aggregated.join(turns, how="left").reset_index()


def _aggregate_sex() -> pd.DataFrame:
    raw = read_raw(5)
    proportions = pd.crosstab(raw["CO_CURSO"], raw["TP_SEXO"], normalize="index")
    proportions.columns = [f"PROP_SEXO_{value}" for value in proportions.columns]
    return proportions.reset_index()


def _aggregate_age() -> pd.DataFrame:
    raw = read_raw(6)
    # 17--89 é a faixa válida documentada; valores nessa faixa não são descartados.
    raw["NU_IDADE"] = raw["NU_IDADE"].where(raw["NU_IDADE"].between(17, 89))
    return raw.groupby("CO_CURSO")["NU_IDADE"].agg(
        IDADE_MEDIA="mean",
        IDADE_MEDIANA="median",
        IDADE_DP="std",
        IDADE_Q25=lambda value: value.quantile(0.25),
        IDADE_Q75=lambda value: value.quantile(0.75),
    ).reset_index()


def _aggregate_question(file_number: int, variable: str) -> pd.DataFrame:
    raw = read_raw(file_number, ["CO_CURSO", variable])
    response_rate = raw.groupby("CO_CURSO")[variable].count().div(raw.groupby("CO_CURSO").size())
    proportions = pd.crosstab(raw["CO_CURSO"], raw[variable], normalize="index")
    proportions.columns = [f"PROP_{variable}_{value}" for value in proportions.columns]
    result = proportions.join(response_rate.rename(f"TX_RESPOSTA_{variable}"), how="outer")
    return result.reset_index()


def _aggregate_course_evaluation() -> pd.DataFrame:
    raw = read_raw(4)
    items = [column for column in raw.columns if column.startswith("QE_I")]
    numeric = raw[items].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.where(numeric.ge(1) & numeric.le(6))  # 7=não sabe; 8=não se aplica.
    raw["AVALIACAO_PROCESSO_ALUNO"] = numeric.mean(axis=1)
    raw["COBERTURA_AVALIACAO_ALUNO"] = numeric.notna().mean(axis=1)
    return raw.groupby("CO_CURSO").agg(
        AVALIACAO_PROCESSO_MEDIA=("AVALIACAO_PROCESSO_ALUNO", "mean"),
        AVALIACAO_PROCESSO_DP=("AVALIACAO_PROCESSO_ALUNO", "std"),
        TX_RESPOSTA_AVALIACAO=("COBERTURA_AVALIACAO_ALUNO", "mean"),
    ).reset_index()


def build_course_dataset(save: bool = True) -> tuple[pd.DataFrame, dict]:
    """Constrói uma linha por curso sem tentar reidentificar estudantes."""
    # Cada arquivo é agregado separado antes do merge porque o INEP
    # embaralhou as linhas de propósito -- não dá pra juntar direto
    dataset, audit = _aggregate_base()
    components = [
        _aggregate_outcome(),
        _aggregate_academic(),
        _aggregate_sex(),
        _aggregate_age(),
        _aggregate_course_evaluation(),
    ]
    components.extend(_aggregate_question(n, var) for n, var in QUESTION_FILES.items())
    for component in components:
        if component["CO_CURSO"].duplicated().any():
            raise ValueError("Agregação gerou CO_CURSO duplicado; união abortada.")
        dataset = dataset.merge(component, on="CO_CURSO", how="left", validate="one_to_one")

    before = len(dataset)
    dataset = dataset.drop_duplicates(subset=["CO_CURSO"]).copy()
    duplicates_removed = before - len(dataset)
    dataset = dataset.loc[dataset["NT_GER_MEDIA_CURSO"].notna()].sort_values("CO_CURSO").reset_index(drop=True)
    audit.update(
        {
            "linhas_antes_filtro_nota": before,
            "linhas_com_nota_valida": len(dataset),
            "duplicatas_curso_removidas": duplicates_removed,
            "colunas_dataset": dataset.shape[1],
            "regra_uniao": "agregar cada arquivo por CO_CURSO antes de unir; nunca unir estudantes",
        }
    )
    if save:
        output = INTERIM_DIR / "enade_2023_cursos_agregado.parquet"
        dataset.to_parquet(output, index=False)
        (INTERIM_DIR / "auditoria_agregacao.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return dataset, audit


def feature_columns(dataset: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Retorna preditores numéricos e categóricos, excluindo IDs e resultados."""
    categorical = [column for column in CATEGORICAL_FEATURES if column in dataset.columns]
    numeric = [
        column
        for column in dataset.columns
        if column not in NON_FEATURE_COLUMNS and column not in categorical
    ]
    return numeric, categorical
