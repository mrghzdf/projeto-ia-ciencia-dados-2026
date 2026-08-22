#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h}"
cd "$PROJECT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Ambiente ainda não preparado. Execute primeiro: ./preparar_ambiente.sh"
  exit 1
fi

export PYTHONPATH="$PROJECT_DIR"
exec .venv/bin/python -m streamlit run app/dashboard.py "$@"
