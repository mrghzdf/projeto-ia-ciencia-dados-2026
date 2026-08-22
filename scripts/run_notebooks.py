"""Executa os quatro notebooks na ordem pedagógica usando o Python do ambiente local."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    ROOT / "notebooks" / "01_aquisicao.ipynb",
    ROOT / "notebooks" / "02_preparacao.ipynb",
    ROOT / "notebooks" / "03_eda.ipynb",
    ROOT / "notebooks" / "04_modelagem.ipynb",
]

for path in NOTEBOOKS:
    print(f"Executando {path.name}...", flush=True)
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=900,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )
    client.execute()
    nbformat.write(notebook, path)
    print(f"Concluído: {path.name}", flush=True)

