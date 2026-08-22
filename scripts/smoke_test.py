"""Valida os artefatos essenciais sem refazer o treinamento."""

from pathlib import Path

import json
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "data" / "processed" / "train_cursos.parquet",
    ROOT / "data" / "processed" / "test_cursos.parquet",
    ROOT / "reports" / "tables" / "metricas_modelos.csv",
    ROOT / "models" / "melhor_modelo.joblib",
]
for path in required:
    assert path.exists() and path.stat().st_size > 0, f"Artefato ausente/vazio: {path}"

metadata = json.loads((ROOT / "data" / "processed" / "metadata_preparacao.json").read_text(encoding="utf-8"))
test = pd.read_parquet(ROOT / "data" / "processed" / "test_cursos.parquet")
features = metadata["numeric_features"] + metadata["categorical_features"]
model = joblib.load(ROOT / "models" / "melhor_modelo.joblib")
predictions = model.predict(test[features].head(10))
probabilities = model.predict_proba(test[features].head(10))[:, 1]
assert len(predictions) == 10 and ((probabilities >= 0) & (probabilities <= 1)).all()
print("Smoke test aprovado: carregamento e inferência do Pipeline completos.")

