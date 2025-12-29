from pathlib import Path
from datetime import datetime

ANIO_TRABAJO = datetime.now().year

BASE_DIR = Path(__file__).resolve().parents[1]   # .../impuestos

OUTPUTS_DIR = BASE_DIR / "outputs"
