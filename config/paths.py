from pathlib import Path
from datetime import datetime

ANIO_TRABAJO = datetime.now().year

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUTS_DIR = BASE_DIR / "outputs"
RAW_DIR = OUTPUTS_DIR / "raw"
NORMALIZED_DIR = OUTPUTS_DIR / "normalized"
