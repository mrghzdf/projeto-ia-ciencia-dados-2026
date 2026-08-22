"""Configurações centrais e caminhos do projeto."""

from pathlib import Path

# Seed fixa pra garantir que o resultado sai igual toda vez
RANDOM_STATE = 42
TEST_SIZE = 0.20
ANO_ENADE = 2023

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "Microdados_Enade_2023"
RAW_DATA_DIR = RAW_ROOT / "DADOS"
RAW_DOCS_DIR = RAW_ROOT / "1.LEIA-ME"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
TABLES_DIR = PROJECT_ROOT / "reports" / "tables"
MODELS_DIR = PROJECT_ROOT / "models"

for directory in (INTERIM_DIR, PROCESSED_DIR, FIGURES_DIR, TABLES_DIR, MODELS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

