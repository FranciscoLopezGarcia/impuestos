from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SOURCES_DIR = BASE_DIR / "sources"
REPORTS_DIR = BASE_DIR / "reports"

KEYWORDS = [
    "Ganancia no imponible",
    "Cónyuge",
    "Hijos",
    "Deducción especial",
    "Gastos de sepelio",
    "Intereses",
    "Primas de seguros",
    "Servicio doméstico",
]

ARCA_URLS = {
    "deducciones_personales": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/deducciones-personales.asp",
    "deducciones_generales": "https://www.arca.gob.ar/gananciasYBienes/ganancias/personas-humanas-sucesiones-indivisas/deducciones/deducciones-generales.asp",
    "bienes_personales": "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/declaracion-jurada/determinativa.asp",
}
