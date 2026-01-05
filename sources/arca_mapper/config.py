from pathlib import Path

# =========================
# SITE CONFIG
# =========================

BASE_DOMAIN = "www.arca.gob.ar"
START_URLS = [
    "https://www.arca.gob.ar/gananciasYBienes/",
    "https://www.arca.gob.ar/gananciasYBienes/ganancias/",
    "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/",
]


MAX_PAGES = 300          # límite total de páginas
MAX_DEPTH = 4            # profundidad de navegación
REQUEST_DELAY = 1.0      # segundos entre requests

USER_AGENT = "PublicData-Explorer/1.0"

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SITE_MAP_JSON = OUTPUT_DIR / "site_map.json"
SUMMARY_TXT = OUTPUT_DIR / "summary.txt"

# =========================
# KEYWORDS
# =========================

KEYWORDS = [
    "ganancia",
    "deducción",
    "deducciones",
    "alícuota",
    "mínimo",
    "exento",
    "escala",
    "bienes",
    "casa habitación",
    "dólar",
    "valuación",
    "inmueble",
]
