#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h}"
cd "$PROJECT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Ambiente ainda não preparado. Execute primeiro: ./preparar_ambiente.sh"
  exit 1
fi

export PYTHONPATH="$PROJECT_DIR"

echo "Executando Aquisição → Preparação → EDA → Modelagem..."
.venv/bin/python -u scripts/run_notebooks.py
.venv/bin/python scripts/smoke_test.py
echo "Pipeline concluído. Para visualizar: ./rodar_dashboard.sh"

