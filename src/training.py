"""Treinamento, tuning, comparação e persistência dos modelos."""

from __future__ import annotations

import json
from time import perf_counter

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
from sklearn.inspection import permutation_importance
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

from src.config import FIGURES_DIR, MODELS_DIR, PROCESSED_DIR, RANDOM_STATE, TABLES_DIR
from src.modeling import build_preprocessor, evaluate_classifier, feature_importance_table
from src.preparation import TARGET_BINARY


def _pipeline(preprocessor, model) -> Pipeline:
    return Pipeline([("preprocessor", clone(preprocessor)), ("model", model)])


def train_and_evaluate() -> tuple[pd.DataFrame, dict]:
    """Seleciona pelo F1 médio de CV e usa teste somente para avaliação final."""
    train = pd.read_parquet(PROCESSED_DIR / "train_cursos.parquet")
    test = pd.read_parquet(PROCESSED_DIR / "test_cursos.parquet")
    metadata = json.loads((PROCESSED_DIR / "metadata_preparacao.json").read_text(encoding="utf-8"))
    numeric = metadata["numeric_features"]
    categorical = metadata["categorical_features"]
    features = numeric + categorical
    X_train, y_train = train[features], train[TARGET_BINARY]
    X_test, y_test = test[features], test[TARGET_BINARY]
    preprocessor = build_preprocessor(numeric, categorical)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    fitted: dict[str, Pipeline] = {}
    rows: list[dict] = []

    # Regressão logística como baseline -- simples e já dá pra interpretar os coeficientes
    baseline = _pipeline(
        preprocessor,
        LogisticRegression(max_iter=2500, class_weight="balanced", random_state=RANDOM_STATE),
    )
    started = perf_counter()
    scores = cross_val_score(baseline, X_train, y_train, scoring="f1", cv=cv, n_jobs=1)
    baseline.fit(X_train, y_train)
    fitted["Regressão Logística"] = baseline
    rows.append(
        {
            "modelo": "Regressão Logística",
            "cv_f1_mean": scores.mean(),
            "cv_f1_std": scores.std(),
            "best_params": "parâmetros padrão documentados",
            "tempo_segundos": perf_counter() - started,
            **evaluate_classifier(baseline, X_test, y_test),
        }
    )

    searches = {
        "Random Forest": (
            _pipeline(
                preprocessor,
                RandomForestClassifier(
                    random_state=RANDOM_STATE,
                    class_weight="balanced",
                    n_jobs=1,
                ),
            ),
            {
                "model__n_estimators": [200, 350, 500],
                "model__max_depth": [None, 10, 18],
                "model__min_samples_leaf": [1, 2, 5],
                "model__max_features": ["sqrt", 0.5],
            },
        ),
        "HistGradientBoosting": (
            _pipeline(
                preprocessor,
                HistGradientBoostingClassifier(
                    random_state=RANDOM_STATE,
                    class_weight="balanced",
                ),
            ),
            {
                "model__max_iter": [150, 250, 350],
                "model__max_leaf_nodes": [15, 31, 63],
                "model__learning_rate": [0.03, 0.06, 0.1],
                "model__l2_regularization": [0.0, 0.1, 1.0],
            },
        ),
    }
    for name, (pipeline, params) in searches.items():
        started = perf_counter()
        search = RandomizedSearchCV(
            pipeline,
            param_distributions=params,
            n_iter=4,
            scoring="f1",
            cv=cv,
            random_state=RANDOM_STATE,
            n_jobs=1,
            refit=True,
            return_train_score=False,
        )
        search.fit(X_train, y_train)
        best = search.best_estimator_
        fitted[name] = best
        rows.append(
            {
                "modelo": name,
                "cv_f1_mean": search.best_score_,
                "cv_f1_std": search.cv_results_["std_test_score"][search.best_index_],
                "best_params": json.dumps(search.best_params_, ensure_ascii=False, sort_keys=True),
                "tempo_segundos": perf_counter() - started,
                **evaluate_classifier(best, X_test, y_test),
            }
        )

    metrics = pd.DataFrame(rows).sort_values("cv_f1_mean", ascending=False).reset_index(drop=True)
    best_name = metrics.loc[0, "modelo"]
    best_pipeline = fitted[best_name]
    joblib.dump(best_pipeline, MODELS_DIR / "melhor_modelo.joblib")
    metrics.to_csv(TABLES_DIR / "metricas_modelos.csv", index=False, encoding="utf-8-sig")

    predictions = pd.DataFrame(
        {
            "CO_CURSO": test["CO_CURSO"].values,
            "y_true": y_test.values,
            "y_pred": best_pipeline.predict(X_test),
            "y_proba": best_pipeline.predict_proba(X_test)[:, 1],
        }
    )
    predictions.to_csv(TABLES_DIR / "predicoes_teste.csv", index=False, encoding="utf-8-sig")
    try:
        importance = feature_importance_table(best_pipeline)
    except TypeError:
        # HistGradientBoosting não expõe feature_importances_; usa-se permutação
        # somente para interpretação pós-avaliação, nunca para selecionar o modelo.
        permutation = permutation_importance(
            best_pipeline,
            X_test,
            y_test,
            scoring="f1",
            n_repeats=8,
            random_state=RANDOM_STATE,
            n_jobs=1,
        )
        importance = pd.DataFrame(
            {"feature": features, "importance": permutation.importances_mean}
        ).sort_values("importance", ascending=False, ignore_index=True)
    importance.to_csv(TABLES_DIR / "importancia_features.csv", index=False, encoding="utf-8-sig")

    model_metadata = {
        "melhor_modelo": best_name,
        "criterio_selecao": "maior F1 médio em validação cruzada estratificada de 5 folds no treino",
        "teste_usado_na_selecao": False,
        "random_state": RANDOM_STATE,
        "target": TARGET_BINARY,
        "features": features,
        "best_params": metrics.loc[0, "best_params"],
    }
    (MODELS_DIR / "metadata_modelo.json").write_text(
        json.dumps(model_metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Comparativo de todas as métricas de teste.
    long_metrics = metrics.melt(
        id_vars="modelo",
        value_vars=["accuracy", "precision", "recall", "f1", "roc_auc"],
        var_name="métrica",
        value_name="valor",
    )
    plt.figure(figsize=(11, 6))
    sns.barplot(data=long_metrics, x="métrica", y="valor", hue="modelo")
    plt.ylim(0, 1)
    plt.title("Comparação dos modelos no conjunto de teste")
    plt.xlabel("Métrica")
    plt.ylabel("Valor")
    plt.legend(title="Modelo", loc="lower right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "modelo_01_comparacao_metricas.png", dpi=160, bbox_inches="tight")
    plt.close()

    # ROC dos três candidatos no mesmo conjunto de teste.
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, estimator in fitted.items():
        RocCurveDisplay.from_estimator(estimator, X_test, y_test, name=name, ax=ax)
    ax.plot([0, 1], [0, 1], "--", color="gray", linewidth=1)
    ax.set_title("Curvas ROC no conjunto de teste")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "modelo_02_curvas_roc.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Matriz de confusão e importâncias do modelo selecionado.
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_estimator(best_pipeline, X_test, y_test, cmap="Blues", ax=ax)
    ax.set_title(f"Matriz de confusão — {best_name}")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "modelo_03_matriz_confusao.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    top = importance.head(20).sort_values("importance")
    plt.figure(figsize=(10, 7))
    sns.barplot(data=top, x="importance", y="feature", color="#4C72B0")
    plt.title(f"20 variáveis mais importantes — {best_name}")
    plt.xlabel("Importância")
    plt.ylabel("Variável transformada")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "modelo_04_importancia_features.png", dpi=160, bbox_inches="tight")
    plt.close()

    return metrics, model_metadata
