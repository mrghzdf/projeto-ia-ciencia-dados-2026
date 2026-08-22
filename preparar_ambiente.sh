#!/bin/zsh
set -euo pipefail

# Sempre trabalha a partir da pasta onde este script está localizado.
PROJECT_DIR="${0:A:h}"
cd "$PROJECT_DIR"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Criando ambiente virtual local em .venv..."
  python3 -m venv .venv
fi

echo "Instalando/verificando dependências somente na .venv do projeto..."
PIP_CACHE_DIR="$PROJECT_DIR/.pip-cache" .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check

echo "Ambiente preparado com sucesso."
echo "Para abrir o dashboard, execute: ./rodar_dashboard.sh"

